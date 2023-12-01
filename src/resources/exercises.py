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
    """
    Manages Exercises.

    `GET` /exercises/{exercises_id}
        Retrieves a single exercise's data using its ID
    `GET` /exercises/date/{exercises_date}
        Retrieves a single exercise's data using its creation date
    `POST` /exercises
        Adds a new exercise entry with:
            minutes: duration of exercise
            description: text describing the activity
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, exercises_id: int):
        """
        Retrieves a single exercise's data using exercise's ID

        `GET` /exercises/{exercises_id}

        Args:
            exercises_id: the exercise's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Exercise's data successfully retrieved
        """
        simpleLogger.info(f"GET /exercises/{exercises_id}")
        exercises = None
        try:
            simpleLogger.debug("Fetching exercises from database using id.")
            exercises = self.uow.repository.get_exercises_by_id(exercises_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch exercises database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the exercise."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not exercises:
            simpleLogger.debug(f"No Exercises data with id {exercises_id}.")
            resp.text = json.dumps(
                {"error": f"No Exercises data with id {exercises_id}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(exercises)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /exercises/{exercises_id} : successful")

    def on_get_date(
        self, req: falcon.Request, resp: falcon.Response, exercises_date: str
    ):
        """
        Retrieves a single exercise's data using exercise's creation date

        `GET` /exercises/date/{exercises_date}

        Args:
            exercises_date: the exercise's creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Exercise's data successfully retrieved
        """
        simpleLogger.info(f"GET /exercises/date/{exercises_date}")
        exercises = None
        try:
            simpleLogger.debug("Formatting the date for exercise.")
            exercises_date = datetime.strptime(exercises_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(
                f"Date {exercises_date} is malformed!", exc_info=True
            )
            resp.text = json.dumps(
                {
                    "error": f"Date {exercises_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching exercises from database using date.")
            exercises = self.uow.repository.get_exercises_by_date(exercises_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch exercises database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the exercise."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not exercises:
            simpleLogger.debug(f"No Exercises data in date {exercises_date}.")
            resp.text = json.dumps(
                {"error": f"No Exercises data in date {exercises_date}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(exercises)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /exercises/date/{exercises_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new exercise

        `POST` /exercises

        Required Body:
            `minutes`: duration of exercise
            `description`: text describing the activity

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: Database error

            `201 CREATED`: Exercise's data successfully added
        """
        simpleLogger.info("POST /exercises")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body.")
            resp.text = json.dumps({"error": "Missing request body."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["date", "minutes", "description"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        if not all(key in body for key in ["minutes", "description"]):
            simpleLogger.debug("Missing Exercises parameter.")
            resp.text = json.dumps({"error": "Missing Exercises parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            exercises = Exercises(**body)
        except Exception as e:
            detailedLogger.error("Could not create a Exercise instance!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": "The server could not create an Exercise with the parameters provided."
                }
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return
        try:
            simpleLogger.debug("Trying to add Exercises data to database.")
            self.uow.repository.add_exercises(exercises)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add exercises to database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not add the exercise."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /exercises : successful")

    def on_delete(self, req: falcon.Request, resp: falcon.Response, exercises_id: int):
        """
        Deletes a single exercise's data using exercise's ID

        `DELETE` /exercises/{exercises_id}

        Args:
            exercises_id: the exercise's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Exercise's data successfully deleted
        """
        simpleLogger.info(f"DELETE /exercises/{exercises_id}")
        exercise = None
        try:
            simpleLogger.debug("Fetching exercise from database using id.")
            exercise = self.uow.repository.get_exercises_by_id(exercises_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch exercise database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the exercise."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not exercise:
            simpleLogger.debug(f"No Exercise data with id {exercises_id}.")
            resp.text = json.dumps(
                {"error": f"No Exercise data with id {exercises_id}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting exercise from database using id.")
            self.uow.repository.delete_exercises(exercise)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete exercise database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not delete the exercise."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /exercises/{exercises_id} : successful")

    def on_delete_date(
        self, req: falcon.Request, resp: falcon.Response, exercise_date: str
    ):
        """
        Deletes a single exercise's data using exercise's creation date

        `DELETE` /exercises/date/{exercise_date}

        Args:
            exercise_date: the exercise's creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `204 No Content`: Exercise's data successfully deleted
        """
        simpleLogger.info(f"DELETE /exercises/date/{exercise_date}")
        exercise = None
        try:
            simpleLogger.debug("Formatting the date for exercise.")
            exercise_date = datetime.strptime(exercise_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {exercise_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {exercise_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching exercise from database using date.")
            exercise = self.uow.repository.get_exercises_by_date(exercise_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch exercise database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the exercise."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not exercise:
            simpleLogger.debug(f"No Exercise data in date {exercise_date}.")
            resp.text = json.dumps(
                {"error": f"No Exercise data in date {exercise_date}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting exercise from database using date.")
            self.uow.repository.delete_exercises(exercise)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete exercise database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not delete the exercise."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /exercises/date/{exercise_date} : successful")
