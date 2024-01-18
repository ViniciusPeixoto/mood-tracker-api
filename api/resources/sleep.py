import json
import logging
import logging.config
from datetime import datetime

import falcon

from api.config.config import get_logging_conf
from api.repository.models import Sleep
from api.resources.base import Resource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class SleepResource(Resource):
    """
    Manages Sleep.

    `GET` /sleep/{sleep_id}
        Retrieves a single sleep's data using its ID
    `GET` /sleep/date/{sleep_date}
        Retrieves all sleeps' data using the creation date
    `POST` /sleep
        Adds a new sleep entry with:
            value: evaluation of sleep
            minutes: duration of sleep
            description: text describing the given grade
    `PATCH` /sleep/{sleep_id}
        Updates a single sleep's data using its ID
    `DELETE` /sleep/{sleep_id}
        Deletes a single sleep's data using its ID
    `DELETE` /sleep/date/{sleep_date}
        Deletes all sleeps' data using the creation date
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, sleep_id: int):
        """
        Retrieves a single sleep's data using its ID

        `GET` /sleep/{sleep_id}

        Args:
            sleep_id: the sleep's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Sleep's data successfully retrieved
        """
        simpleLogger.info(f"GET /sleep/{sleep_id}")
        user = self._get_user(req.context.get("username"))
        sleep = None

        try:
            simpleLogger.debug("Fetching sleep from database using id.")
            sleep = self.uow.repository.get_sleep_by_id(sleep_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch sleep database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not sleep:
            simpleLogger.debug(f"No Sleep data with id {sleep_id}.")
            resp.text = json.dumps({"error": f"No Sleep data with id {sleep_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != sleep.mood.user_id:
            simpleLogger.debug(f"Invalid user for sleep {sleep_id}.")
            resp.text = json.dumps({"error": f"Invalid user for sleep {sleep_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        resp.text = json.dumps(sleep.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /sleep/{sleep_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, sleep_date: str):
        """
        Retrieves all sleeps' data using the creation date

        `GET` /sleep/date/{sleep_date}

        Args:
            sleep_date: the sleeps' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Sleeps' data successfully retrieved
        """
        simpleLogger.info(f"GET /sleep/date/{sleep_date}")
        user = self._get_user(req.context.get("username"))
        sleeps = None

        try:
            simpleLogger.debug("Formatting the date for sleep.")
            sleep_date = datetime.strptime(sleep_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {sleep_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {sleep_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching sleep from database using date.")
            sleeps = self.uow.repository.get_sleep_by_date(sleep_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch sleep database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not sleeps.first():
            simpleLogger.debug(f"No Sleep data in date {sleep_date}.")
            resp.text = json.dumps({"error": f"No Sleep data in date {sleep_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        all_sleeps = {
            sleep.id: sleep.as_dict()
            for sleep in sleeps
            if sleep.mood.user_id == user.id
        }

        resp.text = json.dumps(all_sleeps)
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /sleep/date/{sleep_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new sleep entry

        `POST` /sleep

        Required Body:
            `value`: evaluation of sleep
            `description`: text describing the given grade
            `health_based`: True/False if health issues influenced the given grade

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: Database error

            `201 CREATED`: Sleep's data successfully added
        """
        simpleLogger.info("POST /sleep")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for sleep.")
            resp.text = json.dumps({"error": "Missing request body for sleep."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["date", "value", "minutes", "description"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        if not all(key in body for key in ["value", "minutes", "description"]):
            simpleLogger.debug("Missing Sleep parameter.")
            resp.text = json.dumps({"error": "Missing Sleep parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        sleep_date = body.get("date") or str(datetime.today().date())
        user = self._get_user(req.context.get("username"))
        mood = self._get_mood_from_date(sleep_date, user.id)

        try:
            sleep = Sleep(**body, mood_id=mood.id)
        except Exception as e:
            detailedLogger.error("Could not create a Sleep instance!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": "The server could not create a Sleep with the parameters provided."
                }
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        try:
            simpleLogger.debug("Trying to add Sleep data to database.")
            self.uow.repository.add_sleep(sleep)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add sleep to database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not add the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /sleep : successful")

    def on_patch(self, req: falcon.Request, resp: falcon.Response, sleep_id: int):
        """
        Updates a single sleep's data using its ID

        `PATCH` /sleep/{sleep_id}

        Args:
            sleep_id: the sleep's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Sleep's data successfully updated
        """
        simpleLogger.info(f"PATCH /sleep/{sleep_id}")
        user = self._get_user(req.context.get("username"))
        sleep = None

        try:
            simpleLogger.debug("Fetching sleep from database using id.")
            sleep = self.uow.repository.get_sleep_by_id(sleep_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch sleep database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not sleep:
            simpleLogger.debug(f"No Sleep data with id {sleep_id}.")
            resp.text = json.dumps({"error": f"No Sleep data with id {sleep_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != sleep.mood.user_id:
            simpleLogger.debug(f"Invalid user for exercise {sleep_id}.")
            resp.text = json.dumps({"error": f"Invalid user for exercise {sleep_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for sleep.")
            resp.text = json.dumps({"error": "Missing request body for sleep."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["value", "minutes", "description"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Updating sleep from database using id.")
            self.uow.repository.update_sleep(sleep, body)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform update sleep database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not update the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        updated_sleep = self.uow.repository.get_sleep_by_id(sleep_id)
        resp.text = json.dumps(updated_sleep.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"PATCH /sleep/{sleep_id} : successful")

    def on_delete(self, req: falcon.Request, resp: falcon.Response, sleep_id: int):
        """
        Deletes a single sleep's data using its ID

        `DELETE` /sleep/{sleep_id}

        Args:
            sleep_id: the sleep's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Sleep's data successfully deleted
        """
        simpleLogger.info(f"DELETE /sleep/{sleep_id}")
        user = self._get_user(req.context.get("username"))
        sleep = None

        try:
            simpleLogger.debug("Fetching sleep from database using id.")
            sleep = self.uow.repository.get_sleep_by_id(sleep_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch sleep database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not sleep:
            simpleLogger.debug(f"No Sleep data with id {sleep_id}.")
            resp.text = json.dumps({"error": f"No Sleep data with id {sleep_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != sleep.mood.user_id:
            simpleLogger.debug(f"Invalid user for sleep {sleep_id}.")
            resp.text = json.dumps({"error": f"Invalid user for sleep {sleep_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        try:
            simpleLogger.debug("Deleting sleep from database using id.")
            self.uow.repository.delete_sleep(sleep)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete sleep database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /sleep/{sleep_id} : successful")

    def on_delete_date(
        self, req: falcon.Request, resp: falcon.Response, sleep_date: str
    ):
        """
        Deletes all sleeps' data using the creation date

        `DELETE` /sleep/date/{sleep_date}

        Args:
            sleep_date: the sleeps' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `204 No Content`: Sleeps' data successfully deleted
        """
        simpleLogger.info(f"DELETE /sleep/date/{sleep_date}")
        user = self._get_user(req.context.get("username"))
        sleeps = None

        try:
            simpleLogger.debug("Formatting the date for sleep.")
            sleep_date = datetime.strptime(sleep_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {sleep_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {sleep_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching sleeps from database using date.")
            sleeps = self.uow.repository.get_sleep_by_date(sleep_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch sleep database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the sleep."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not sleeps.first():
            simpleLogger.debug(f"No Sleep data in date {sleep_date}.")
            resp.text = json.dumps({"error": f"No Sleep data in date {sleep_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting sleep from database using date.")
            for sleep in sleeps:
                if user.id != sleep.mood.user_id:
                    simpleLogger.debug(f"Invalid user for sleep {sleep.id}.")
                    resp.text = json.dumps(
                        {"error": f"Invalid user for sleep {sleep.id}."}
                    )
                    resp.status = falcon.HTTP_FORBIDDEN
                    self.uow.rollback()
                    return
                self.uow.repository.delete_sleep(sleep)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete sleeps database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the sleeps."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /sleep/date/{sleep_date} : successful")
