import json
import logging
import logging.config
from datetime import datetime

import falcon

from api.repository.models import Water
from api.resources.base import Resource
from api.config.config import get_logging_conf

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class WaterResource(Resource):
    """
    Manages Water Intake.

    `GET` /water-intake/{water_intake_id}
        Retrieves a single water intake's data using its ID
    `GET` /water-intake/date/{water_intake_date}
        Retrieves a single water intake's data using its creation date
    `POST` /water-intake
        Adds a new water intake entry with:
            milliliters: volume of water consumed, in ml
            description: text describing issues for consumption
            pee: True/False if there was excessive peeing during the day
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, water_intake_id: int):
        """
        Retrieves a single water intake's data using water intake's ID

        `GET` /water-intake/{water_intake_id}

        Args:
            water_intake_id: the water intake's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Water intake's data successfully retrieved
        """
        simpleLogger.info(f"GET /water-intake/{water_intake_id}")
        water_intake = None

        try:
            simpleLogger.debug("Fetching water intake from database using id.")
            water_intake = self.uow.repository.get_water_intake_by_id(water_intake_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch water intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the water intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not water_intake:
            simpleLogger.debug(f"No Water data with id {water_intake_id}.")
            resp.text = json.dumps(
                {"error": f"No Water data with id {water_intake_id}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(water_intake)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /water-intake/{water_intake_id} : successful")

    def on_get_date(
        self, req: falcon.Request, resp: falcon.Response, water_intake_date: str
    ):
        """
        Retrieves all water intakes' data using water intakes' creation date

        `GET` /water-intake/date/{water_intake_date}

        Args:
            water_intake_date: the water intakes' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Water intakes' data successfully retrieved
        """
        simpleLogger.info(f"GET /water-intake/date/{water_intake_date}")
        water_intakes = None

        try:
            simpleLogger.debug("Formatting the date for water intake.")
            water_intake_date = datetime.strptime(water_intake_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(
                f"Date {water_intake_date} is malformed!", exc_info=True
            )
            resp.text = json.dumps(
                {
                    "error": f"Date {water_intake_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching water intake from database using date.")
            water_intakes = self.uow.repository.get_water_intake_by_date(
                water_intake_date
            )
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch water intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the water intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not water_intakes.first():
            simpleLogger.debug(f"No Water data in date {water_intake_date}.")
            resp.text = json.dumps(
                {"error": f"No Water data in date {water_intake_date}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        all_water_intakes = {water_intake.id: json.loads(str(water_intake)) for water_intake in water_intakes}

        resp.text = json.dumps(all_water_intakes)
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /water-intake/date/{water_intake_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new water intake

        `POST` /water-intake

        Required Body:
            `milliliters`: volume of water consumed, in ml
            `description`: text describing issues for consumption
            `pee`: True/False if there was excessive peeing during the day

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: Database error

            `201 CREATED`: Water intake's data successfully added
        """
        simpleLogger.info("POST /water-intake")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for water intake.")
            resp.text = json.dumps({"error": "Missing request body for water intake."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["date", "milliliters", "description", "pee"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        if not all(key in body for key in ["milliliters", "description", "pee"]):
            simpleLogger.debug("Missing Water parameter.")
            resp.text = json.dumps({"error": "Missing Water parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            water_intake = Water(**body)
        except Exception as e:
            detailedLogger.error(
                "Could not create a Water Intake instance!", exc_info=True
            )
            resp.text = json.dumps(
                {
                    "error": "The server could not create a Water Intake with the parameters provided."
                }
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        try:
            simpleLogger.debug("Trying to add Water data to database.")
            self.uow.repository.add_water_intake(water_intake)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add water intake to database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not add the water intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /water-intake: successful")

    def on_patch(
        self, req: falcon.Request, resp: falcon.Response, water_intake_id: int
    ):
        """
        Updates a single water intake's data using water intake's ID

        `PATCH` /water-intake/{water_intake_id}

        Args:
            water_intake_id: the water intake's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Exercises's data successfully updated
        """
        simpleLogger.info(f"PATCH /water-intake/{water_intake_id}")
        water_intake = None

        try:
            simpleLogger.debug("Fetching water intake from database using id.")
            water_intake = self.uow.repository.get_water_intake_by_id(water_intake_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch water intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the water intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for water intake.")
            resp.text = json.dumps({"error": "Missing request body for water intake."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["milliliters", "description", "pee"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Updating water intake from database using id.")
            self.uow.repository.update_water_intake(water_intake, body)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform update water intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not update the water intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        updated_water_intake = self.uow.repository.get_water_intake_by_id(
            water_intake_id
        )
        resp.text = json.dumps(json.loads(str(updated_water_intake)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"PATCH /water-intake/{water_intake_id} : successful")

    def on_delete(
        self, req: falcon.Request, resp: falcon.Response, water_intake_id: int
    ):
        """
        Deletes a single water_intake's data using water_intake's ID

        `DELETE` /water-intake/{water_intake_id}

        Args:
            water_intake_id: the water_intake's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Water Intake's data successfully deleted
        """
        simpleLogger.info(f"DELETE /water-intake/{water_intake_id}")
        water_intake = None

        try:
            simpleLogger.debug("Fetching water_intake from database using id.")
            water_intake = self.uow.repository.get_water_intake_by_id(water_intake_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch water_intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the water_intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not water_intake:
            simpleLogger.debug(f"No Water Intake data with id {water_intake_id}.")
            resp.text = json.dumps(
                {"error": f"No Water Intake data with id {water_intake_id}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting water_intake from database using id.")
            self.uow.repository.delete_water_intake(water_intake)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete water_intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not delete the water_intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /water-intake/{water_intake_id} : successful")

    def on_delete_date(
        self, req: falcon.Request, resp: falcon.Response, water_intake_date: str
    ):
        """
        Deletes all water_intakes' data using water_intakes' creation date

        `DELETE` /water-intake/date/{water_intake_date}

        Args:
            water_intake_date: the water_intakes' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `204 No Content`: Water Intakes' data successfully deleted
        """
        simpleLogger.info(f"DELETE /water-intake/date/{water_intake_date}")
        water_intakes = None

        try:
            simpleLogger.debug("Formatting the date for water_intake.")
            water_intake_date = datetime.strptime(water_intake_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(
                f"Date {water_intake_date} is malformed!", exc_info=True
            )
            resp.text = json.dumps(
                {
                    "error": f"Date {water_intake_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching water_intake from database using date.")
            water_intakes = self.uow.repository.get_water_intake_by_date(
                water_intake_date
            )
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch water_intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the water_intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not water_intakes.first():
            simpleLogger.debug(f"No Water Intake data in date {water_intake_date}.")
            resp.text = json.dumps(
                {"error": f"No Water Intake data in date {water_intake_date}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting water_intake from database using date.")
            for water_intake in water_intakes:
                self.uow.repository.delete_water_intake(water_intake)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete water_intake database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not delete the water_intake."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /water-intake/date/{water_intake_date} : successful")