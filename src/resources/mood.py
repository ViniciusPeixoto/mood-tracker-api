import json
import logging
import logging.config
from collections import namedtuple
from datetime import datetime

import falcon

from src.repository.models import Exercises, Food, Humor, Mood, Water
from src.resources.base import Resource

logging.config.fileConfig("src/utils/logging.conf")
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class MoodResource(Resource):
    """
    Manages Mood.

    `GET` /mood/{mood_id}
        Retrieves a single mood's data using its ID
    `GET` /mood/date/{mood_date}
        Retrieves a single mood's data using its creation date
    `POST` /mood
        Adds a new mood entry with:
            exercises: data for exercises entry
            food_habits: data for food habits entry
            humor: data for humor entry
            water_intake: data for water intake entry
    `POST` /mood/date/{mood_date}
        Adds a new mood entry for a given date using pre-existing data for the date
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
        """
        Retrieves a single mood's data using mood's ID

        `GET` /mood/{mood_id}

        Args:
            mood_id: the mood's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Mood's data successfully retrieved
        """
        simpleLogger.info(f"GET /mood/{mood_id}")
        mood = None

        try:
            simpleLogger.debug("Fetching mood from database using id.")
            mood = self.uow.repository.get_mood_by_id(mood_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not mood:
            simpleLogger.debug(f"No Mood data with id {mood_id}.")
            resp.text = json.dumps({"error": f"No Mood data with id {mood_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(mood)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /mood/{mood_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, mood_date: str):
        """
        Retrieves all mood's data using moods' creation date

        `GET` /mood/date/{mood_date}

        Args:
            mood_date: the moods' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: moods' data successfully retrieved
        """
        simpleLogger.info(f"GET /mood/date/{mood_date}")
        moods = None

        try:
            simpleLogger.debug("Formatting the date for mood.")
            mood_date = datetime.strptime(mood_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {mood_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {mood_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching mood from database using date.")
            moods = self.uow.repository.get_mood_by_date(mood_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not moods.first():
            simpleLogger.debug(f"No Mood data in date {mood_date}.")
            resp.text = json.dumps({"error": f"No Mood data in date {mood_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        all_moods = {mood.id: str(mood) for mood in moods}

        resp.text = json.dumps(all_moods)
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /mood/date/{mood_date} : successful")

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new mood

        `POST` /mood

        Required Body:
            `minutes`: duration of exercise
            `description`: text describing the activity

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: The server could not create a Mood instance

            `500 Server Error`: Database error

            `201 CREATED`: Mood's data successfully added
        """
        simpleLogger.info("POST /mood")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for mood.")
            resp.text = json.dumps({"error": "Missing request body for mood."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["date", "humor", "water_intake", "exercises", "food_habits"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        params_classes = {
            "humor": Humor,
            "water_intake": Water,
            "exercises": Exercises,
            "food_habits": Food,
        }

        try:
            mood_params = {
                key: params_classes.get(key)(**body.get(key))
                for key in ["humor", "water_intake", "exercises", "food_habits"]
            }
        except TypeError as e:
            detailedLogger.warning("Missing Mood parameter.")
            resp.text = json.dumps({"error": "Missing Mood parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        if body.get("date"):
            mood_params["date"] = body.get("date")

        try:
            simpleLogger.debug("Trying to create a Mood instance.")
            mood = Mood(**mood_params)
            mood_params["mood"] = mood
        except TypeError as e:
            detailedLogger.error("Could not create a Mood instance!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": "The server could not create a Mood with the parameters provided."
                }
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        params_db_functions = {
            "humor": self.uow.repository.add_humor,
            "water_intake": self.uow.repository.add_water_intake,
            "exercises": self.uow.repository.add_exercises,
            "food_habits": self.uow.repository.add_food_habits,
            "mood": self.uow.repository.add_mood,
        }

        for key in ["humor", "water_intake", "exercises", "food_habits", "mood"]:
            try:
                simpleLogger.debug(
                    f"Trying to add {key.title().replace('_', ' ')} data to database."
                )
                params_db_functions[key](mood_params[key])
                self.uow.commit()
            except Exception as e:
                detailedLogger.error(
                    f"Could not perform add {key.title().replace('_', ' ')} to database operation!",
                    exc_info=True,
                )
                resp.text = json.dumps(
                    {"error": f"The server could not add the {key.replace('_', ' ')}."}
                )
                resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
                return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /mood : successful")

    def on_post_date(self, req: falcon.Request, resp: falcon.Response, mood_date: str):
        """
        Adds a new mood entry for a given date using pre-existing data for the date.

        `POST` /mood/date/{mood_date}

        Args:
            mood_date: teh date to fetch data and save Mood

        Responses:
            `400 Bad Request`: Date could not be parsed

            `500 Server Error`: The server could not create a Mood instance

            `500 Server Error`: Database error

            `201 CREATED`: Mood's data successfully added
        """
        simpleLogger.info(f"POST /mood/date/{mood_date}")

        try:
            simpleLogger.debug("Formatting the date for post mood.")
            mood_date = datetime.strptime(mood_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {mood_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {mood_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Building a Mood instance from multiple dates.")
            mood = self.build_mood(date=mood_date)
        except ValueError as e:
            detailedLogger.warning(
                f"Date {mood_date} does not contain data!", exc_info=True
            )
            resp.text = json.dumps({"error": e.__str__()})
            resp.status = falcon.HTTP_NOT_FOUND
            return
        except Exception as e:
            detailedLogger.error("Could not build Mood.", exc_info=True)
            resp.text = json.dumps(
                {"error": "The server could not build a Mood instance."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        try:
            simpleLogger.debug("Trying to add Mood from date data to database.")
            self.uow.repository.add_mood(mood)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add mood from date to database operation!",
                exc_info=True,
            )
            resp.text = json.dumps({"error": "The server could not add the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info(f"POST /mood/date/{mood_date}")

    def build_mood(self, date: datetime) -> Mood:
        """
        Creates a Mood instance for a given `date` by retrieving data from all parameters
        for this date.

        Args:
            date: the date to fetch data and create Mood instance

        Returns:
            a Mood instance.
        """
        simpleLogger.info(f"Building Mood with data from {date}")
        empty_params = []
        mood = Mood(date=date)

        for param in ["humor", "water_intake", "exercises", "food_habits"]:
            function_name = f"get_{param}_by_date"
            db_function = getattr(self.uow.repository, function_name)

            param_instances = db_function(date)
            if not param_instances.first():
                empty_params.append(param)
                continue

            for param_instance in param_instances:
                setattr(mood, param, param_instance)

        if empty_params:
            raise ValueError(
                f"Date {date} does not contain data for params {empty_params}."
            )

        return mood

    def on_patch(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
        """
        Updates a single mood's data using mood's ID

        `PATCH` /mood/{mood_id}

        Args:
            mood_id: the mood's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Humor's data successfully updated
        """
        simpleLogger.info(f"PATCH /mood/{mood_id}")
        mood = None
        try:
            simpleLogger.debug("Fetching mood from database using id.")
            mood = self.uow.repository.get_mood_by_id(mood_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for mood.")
            resp.text = json.dumps({"error": "Missing request body for mood."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["humor", "water_intake", "exercises", "food_habits"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        params_classes = {
            "humor": Humor,
            "water_intake": Water,
            "exercises": Exercises,
            "food_habits": Food,
        }
        try:
            mood_params = {
                key: params_classes.get(key)(**body.get(key)) for key in body
            }
        except TypeError as e:
            detailedLogger.warning("Missing Mood parameter.")
            resp.text = json.dumps({"error": "Missing Mood parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Updating mood from database using id.")
            for key in mood_params:
                update_function = getattr(self.uow.repository, f"update_{key}")
                update_param = getattr(mood, key)
                simpleLogger.debug(
                    f"Updating {key.replace('_', ' ')} from database using id."
                )
                update_function(update_param, body[key])
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform update mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not update the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        updated_mood = self.uow.repository.get_mood_by_id(mood_id)
        resp.text = json.dumps(json.loads(str(updated_mood)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"PATCH /mood/{mood_id} : successful")

    def on_delete(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
        """
        Deletes a single mood's data using mood's ID

        `DELETE` /mood/{mood_id}

        Args:
            mood_id: the mood's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Mood's data successfully deleted
        """
        simpleLogger.info(f"DELETE /mood/{mood_id}")
        mood = None
        try:
            simpleLogger.debug("Fetching mood from database using id.")
            mood = self.uow.repository.get_mood_by_id(mood_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not mood:
            simpleLogger.debug(f"No Mood data with id {mood_id}.")
            resp.text = json.dumps({"error": f"No Mood data with id {mood_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting mood from database using id.")
            self.uow.repository.delete_mood(mood)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /mood/{mood_id} : successful")

    def on_delete_date(
        self, req: falcon.Request, resp: falcon.Response, mood_date: str
    ):
        """
        Deletes all moods' data using moods' creation date

        `DELETE` /mood/date/{mood_date}

        Args:
            mood_date: the moods' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `204 No Content`: Moods' data successfully deleted
        """
        simpleLogger.info(f"DELETE /mood/date/{mood_date}")
        moods = None

        try:
            simpleLogger.debug("Formatting the date for mood.")
            mood_date = datetime.strptime(mood_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {mood_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {mood_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching mood from database using date.")
            moods = self.uow.repository.get_mood_by_date(mood_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not moods.first():
            simpleLogger.debug(f"No Mood data in date {mood_date}.")
            resp.text = json.dumps({"error": f"No Mood data in date {mood_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting mood from database using date.")
            for mood in moods:
                self.uow.repository.delete_mood(mood)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete moods database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the moods."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /mood/date/{mood_date} : successful")
