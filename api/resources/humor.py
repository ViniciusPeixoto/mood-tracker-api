import json
import logging
import logging.config
from datetime import datetime

import falcon

from api.config.config import get_logging_conf
from api.repository.models import Humor
from api.resources.base import Resource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class HumorResource(Resource):
    """
    Manages Humor.

    `GET` /humor/{humor_id}
        Retrieves a single humor's data using its ID
    `GET` /humor/date/{humor_date}
        Retrieves all humors' data using the creation date
    `POST` /humor
        Adds a new humor entry with:
            value: evaluation of humor
            description: text describing the given grade
            health_based: True/False if health issues influenced the given grade
    `PATCH` /humor/{humor_id}
        Updates a single humor's data using its ID
    `DELETE` /humor/{humor_id}
        Deletes a single humor's data using its ID
    `DELETE` /humor/date/{humor_date}
        Deletes all humors' data using the creation date
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, humor_id: int):
        """
        Retrieves a single humor's data using its ID

        `GET` /humor/{humor_id}

        Args:
            humor_id: the humor's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Humor's data successfully retrieved
        """
        simpleLogger.info(f"GET /humor/{humor_id}")
        user = self._get_user(req.context.get("username"))
        humor = None

        try:
            simpleLogger.debug("Fetching humor from database using id.")
            humor = self.uow.repository.get_humor_by_id(humor_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch humor database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not humor:
            simpleLogger.debug(f"No Humor data with id {humor_id}.")
            resp.text = json.dumps({"error": f"No Humor data with id {humor_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != humor.mood.user_id:
            simpleLogger.debug(f"Invalid user for humor {humor_id}.")
            resp.text = json.dumps({"error": f"Invalid user for humor {humor_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        resp.text = json.dumps(humor.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /humor/{humor_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, humor_date: str):
        """
        Retrieves all humors' data using the creation date

        `GET` /humor/date/{humor_date}

        Args:
            humor_date: the humors' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Humors' data successfully retrieved
        """
        simpleLogger.info(f"GET /humor/date/{humor_date}")
        user = self._get_user(req.context.get("username"))
        humors = None

        try:
            simpleLogger.debug("Formatting the date for humor.")
            humor_date = datetime.strptime(humor_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {humor_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {humor_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching humor from database using date.")
            humors = self.uow.repository.get_humor_by_date(humor_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch humor database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not humors.first():
            simpleLogger.debug(f"No Humor data in date {humor_date}.")
            resp.text = json.dumps({"error": f"No Humor data in date {humor_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        all_humors = {
            humor.id: humor.as_dict()
            for humor in humors
            if humor.mood.user_id == user.id
        }

        resp.text = json.dumps(all_humors)
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /humor/date/{humor_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new humor entry

        `POST` /humor

        Required Body:
            `value`: evaluation of humor
            `description`: text describing the given grade
            `health_based`: True/False if health issues influenced the given grade

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: Database error

            `201 CREATED`: Humor's data successfully added
        """
        simpleLogger.info("POST /humor")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for humor.")
            resp.text = json.dumps({"error": "Missing request body for humor."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["date", "value", "description", "health_based"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        if not all(key in body for key in ["value", "description", "health_based"]):
            simpleLogger.debug("Missing Humor parameter.")
            resp.text = json.dumps({"error": "Missing Humor parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        humor_date = body.get("date") or str(datetime.today().date())
        user = self._get_user(req.context.get("username"))
        mood = self._get_mood_from_date(humor_date, user.id)

        try:
            humor = Humor(**body, mood_id=mood.id)
        except Exception as e:
            detailedLogger.error("Could not create a Humor instance!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": "The server could not create a Humor with the parameters provided."
                }
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        try:
            simpleLogger.debug("Trying to add Humor data to database.")
            self.uow.repository.add_humor(humor)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add humor to database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not add the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /humor : successful")

    def on_patch(self, req: falcon.Request, resp: falcon.Response, humor_id: int):
        """
        Updates a single humor's data using its ID

        `PATCH` /humor/{humor_id}

        Args:
            humor_id: the humor's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Humor's data successfully updated
        """
        simpleLogger.info(f"PATCH /humor/{humor_id}")
        user = self._get_user(req.context.get("username"))
        humor = None

        try:
            simpleLogger.debug("Fetching humor from database using id.")
            humor = self.uow.repository.get_humor_by_id(humor_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch humor database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not humor:
            simpleLogger.debug(f"No Humor data with id {humor_id}.")
            resp.text = json.dumps({"error": f"No Humor data with id {humor_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != humor.mood.user_id:
            simpleLogger.debug(f"Invalid user for exercise {humor_id}.")
            resp.text = json.dumps({"error": f"Invalid user for exercise {humor_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for humor.")
            resp.text = json.dumps({"error": "Missing request body for humor."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["value", "description", "health_based"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Updating humor from database using id.")
            self.uow.repository.update_humor(humor, body)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform update humor database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not update the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        updated_humor = self.uow.repository.get_humor_by_id(humor_id)
        resp.text = json.dumps(updated_humor.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"PATCH /humor/{humor_id} : successful")

    def on_delete(self, req: falcon.Request, resp: falcon.Response, humor_id: int):
        """
        Deletes a single humor's data using its ID

        `DELETE` /humor/{humor_id}

        Args:
            humor_id: the humor's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Humor's data successfully deleted
        """
        simpleLogger.info(f"DELETE /humor/{humor_id}")
        user = self._get_user(req.context.get("username"))
        humor = None

        try:
            simpleLogger.debug("Fetching humor from database using id.")
            humor = self.uow.repository.get_humor_by_id(humor_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch humor database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not humor:
            simpleLogger.debug(f"No Humor data with id {humor_id}.")
            resp.text = json.dumps({"error": f"No Humor data with id {humor_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != humor.mood.user_id:
            simpleLogger.debug(f"Invalid user for humor {humor_id}.")
            resp.text = json.dumps({"error": f"Invalid user for humor {humor_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        try:
            simpleLogger.debug("Deleting humor from database using id.")
            self.uow.repository.delete_humor(humor)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete humor database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /humor/{humor_id} : successful")

    def on_delete_date(
        self, req: falcon.Request, resp: falcon.Response, humor_date: str
    ):
        """
        Deletes all humors' data using the creation date

        `DELETE` /humor/date/{humor_date}

        Args:
            humor_date: the humors' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `204 No Content`: Humors' data successfully deleted
        """
        simpleLogger.info(f"DELETE /humor/date/{humor_date}")
        user = self._get_user(req.context.get("username"))
        humors = None

        try:
            simpleLogger.debug("Formatting the date for humor.")
            humor_date = datetime.strptime(humor_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {humor_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {humor_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching humors from database using date.")
            humors = self.uow.repository.get_humor_by_date(humor_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch humor database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not humors.first():
            simpleLogger.debug(f"No Humor data in date {humor_date}.")
            resp.text = json.dumps({"error": f"No Humor data in date {humor_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting humor from database using date.")
            for humor in humors:
                if user.id != humor.mood.user_id:
                    simpleLogger.debug(f"Invalid user for humor {humor.id}.")
                    resp.text = json.dumps(
                        {"error": f"Invalid user for humor {humor.id}."}
                    )
                    resp.status = falcon.HTTP_FORBIDDEN
                    self.uow.rollback()
                    return
                self.uow.repository.delete_humor(humor)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete humors database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the humors."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /humor/date/{humor_date} : successful")
