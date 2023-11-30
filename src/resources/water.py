import json
import logging
import logging.config
from datetime import datetime

import falcon

from src.repository.models import Water
from src.resources.base import Resource

logging.config.fileConfig("src/utils/logging.conf")
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
        Retrieves a single water intake's data using water intake's creation date

        `GET` /water-intake/date/{water_intake_date}

        Args:
            water_intake_date: the water intake's creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Water intake's data successfully retrieved
        """
        simpleLogger.info(f"GET /water-intake/date/{water_intake_date}")
        water_intake = None
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
            water_intake = self.uow.repository.get_water_intake_by_date(
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

        if not water_intake:
            simpleLogger.debug(f"No Water data in date {water_intake_date}.")
            resp.text = json.dumps(
                {"error": f"No Water data in date {water_intake_date}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(water_intake)))
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
