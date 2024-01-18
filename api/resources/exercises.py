import json
import logging
import logging.config
from datetime import datetime

import falcon

from api.config.config import get_logging_conf
from api.repository.models import Exercises
from api.resources.base import Resource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class ExercisesResource(Resource):
    """
    Manages Exercises.

    `GET` /exercises/{exercises_id}
        Retrieves a single exercise's data using its ID
    `GET` /exercises/date/{exercises_date}
        Retrieves all exercises' data using the creation date
    `POST` /exercises
        Adds a new exercise entry with:
            minutes: duration of exercise
            description: text describing the activity
    `PATCH` /exercises/{exercises_id}
        Updates a single exercises's data using its ID
    `DELETE` /exercises/{exercises_id}
        Deletes a single exercise's data using its ID
    `DELETE` /exercises/date/{exercises_date}
        Deletes all exercises' data using the creation date
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, exercises_id: int):
        """
        Retrieves a single exercise's data using its ID

        `GET` /exercises/{exercises_id}

        Args:
            exercises_id: the exercise's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Exercise's data successfully retrieved
        """
        simpleLogger.info(f"GET /exercises/{exercises_id}")
        user = self._get_user(req.context.get("username"))
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
            return

        if not exercises:
            simpleLogger.debug(f"No Exercises data with id {exercises_id}.")
            resp.text = json.dumps(
                {"error": f"No Exercises data with id {exercises_id}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != exercises.mood.user_id:
            simpleLogger.debug(f"Invalid user for exercise {exercises_id}.")
            resp.text = json.dumps(
                {"error": f"Invalid user for exercise {exercises_id}."}
            )
            resp.status = falcon.HTTP_FORBIDDEN
            return

        resp.text = json.dumps(exercises.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /exercises/{exercises_id} : successful")

    def on_get_date(
        self, req: falcon.Request, resp: falcon.Response, exercises_date: str
    ):
        """
        Retrieves all exercises' data using the creation date

        `GET` /exercises/date/{exercises_date}

        Args:
            exercises_date: the exercises' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Exercises' data successfully retrieved
        """
        simpleLogger.info(f"GET /exercises/date/{exercises_date}")
        user = self._get_user(req.context.get("username"))
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
                {"error": "The server could not fetch the exercises."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not exercises.first():
            simpleLogger.debug(f"No Exercises data in date {exercises_date}.")
            resp.text = json.dumps(
                {"error": f"No Exercises data in date {exercises_date}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        all_exercises = {
            exercise.id: exercise.as_dict()
            for exercise in exercises
            if exercise.mood.user_id == user.id
        }

        resp.text = json.dumps(all_exercises)
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /exercises/date/{exercises_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new exercise entry

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

        exercise_date = body.get("date") or str(datetime.today().date())
        user = self._get_user(req.context.get("username"))
        mood = self._get_mood_from_date(exercise_date, user.id)

        try:
            exercise = Exercises(**body, mood_id=mood.id)
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
            self.uow.repository.add_exercises(exercise)
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

    def on_patch(self, req: falcon.Request, resp: falcon.Response, exercises_id: int):
        """
        Updates a single exercises's data using its ID

        `PATCH` /exercises/{exercises_id}

        Args:
            exercises_id: the exercises's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Exercises's data successfully updated
        """
        simpleLogger.info(f"PATCH /exercises/{exercises_id}")
        user = self._get_user(req.context.get("username"))
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
                {"error": "The server could not fetch the exercises."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not exercises:
            simpleLogger.debug(f"No Exercises data with id {exercises_id}.")
            resp.text = json.dumps(
                {"error": f"No Exercises data with id {exercises_id}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != exercises.mood.user_id:
            simpleLogger.debug(f"Invalid user for exercise {exercises_id}.")
            resp.text = json.dumps(
                {"error": f"Invalid user for exercise {exercises_id}."}
            )
            resp.status = falcon.HTTP_FORBIDDEN
            return

        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for exercises.")
            resp.text = json.dumps({"error": "Missing request body for exercises."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["minutes", "description"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Updating exercises from database using id.")
            self.uow.repository.update_exercises(exercises, body)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform update exercises database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not update the exercises."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        updated_exercises = self.uow.repository.get_exercises_by_id(exercises_id)

        resp.text = json.dumps(updated_exercises.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"PATCH /exercises/{exercises_id} : successful")

    def on_delete(self, req: falcon.Request, resp: falcon.Response, exercises_id: int):
        """
        Deletes a single exercise's data using its ID

        `DELETE` /exercises/{exercises_id}

        Args:
            exercises_id: the exercise's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Exercise's data successfully deleted
        """
        simpleLogger.info(f"DELETE /exercises/{exercises_id}")
        user = self._get_user(req.context.get("username"))
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

        if user.id != exercise.mood.user_id:
            simpleLogger.debug(f"Invalid user for exercise {exercises_id}.")
            resp.text = json.dumps(
                {"error": f"Invalid user for exercise {exercises_id}."}
            )
            resp.status = falcon.HTTP_FORBIDDEN
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
        self, req: falcon.Request, resp: falcon.Response, exercises_date: str
    ):
        """
        Deletes all exercises' data using the creation date

        `DELETE` /exercises/date/{exercises_date}

        Args:
            exercises_date: the exercises' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `204 No Content`: Exercises' data successfully deleted
        """
        simpleLogger.info(f"DELETE /exercises/date/{exercises_date}")
        user = self._get_user(req.context.get("username"))
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
            simpleLogger.debug("Fetching exercise from database using date.")
            exercises = self.uow.repository.get_exercises_by_date(exercises_date)
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

        if not exercises.first():
            simpleLogger.debug(f"No Exercise data in date {exercises_date}.")
            resp.text = json.dumps(
                {"error": f"No Exercise data in date {exercises_date}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting exercises from database using date.")
            for exercise in exercises:
                if user.id != exercise.mood.user_id:
                    simpleLogger.debug(f"Invalid user for exercise {exercise.id}.")
                    resp.text = json.dumps(
                        {"error": f"Invalid user for exercise {exercise.id}."}
                    )
                    resp.status = falcon.HTTP_FORBIDDEN
                    self.uow.rollback()
                    return
                self.uow.repository.delete_exercises(exercise)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete exercise database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not delete the exercises."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /exercises/date/{exercises_date} : successful")
