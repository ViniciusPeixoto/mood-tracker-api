import json
import logging
import logging.config
from datetime import datetime

import falcon

from src.repository.models import Exercises
from src.resources.base import Resource

logging.config.fileConfig("src/utils/logging.conf")
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class ExercisesResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, exercises_id: int):
        simpleLogger.info(f"GET /exercises/{exercises_id}")
        exercises = None
        try:
            simpleLogger.debug("Fetching exercises from database using id.")
            exercises = self.uow.repository.get_exercises_by_id(exercises_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform fetch exercises database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not fetch the exercise."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not exercises:
            simpleLogger.debug(f"No Exercises data with id {exercises_id}.")
            resp.body = json.dumps({"error": f"No Exercises data with id {exercises_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(exercises)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /exercises/{exercises_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, exercises_date: str):
        simpleLogger.info(f"GET /exercises/date/{exercises_date}")
        exercises = None
        try:
            simpleLogger.debug("Formatting the date for exercise.")
            exercises_date = datetime.strptime(exercises_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {exercises_date} is malformed!", exc_info=True)
            resp.body = json.dumps({"error": f"Date {exercises_date} is malformed! Correct format is YYYY-MM-DD."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching exercises from database using date.")
            exercises = self.uow.repository.get_exercises_by_date(exercises_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform fetch exercises database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not fetch the exercise."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not exercises:
            simpleLogger.debug(f"No Exercises data in date {exercises_date}.")
            resp.body = json.dumps({"error": f"No Exercises data in date {exercises_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(exercises)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /exercises/date/{exercises_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        simpleLogger.info("POST /exercises")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body.")
            resp.body = json.dumps({"error": "Missing request body."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        exercises_minutes = body.get("minutes")
        exercises_description = body.get("description")

        if not all((exercises_minutes, exercises_description)):
            simpleLogger.debug("Missing Exercises parameter.")
            resp.body = json.dumps({"error": "Missing Exercises parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        exercises = Exercises(
            minutes=exercises_minutes, description=exercises_description
        )
        try:
            simpleLogger.debug("Trying to add Exercises data to database.")
            self.uow.repository.add_exercises(exercises)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform add exercises to database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not add the exercise."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /exercises : successful")
