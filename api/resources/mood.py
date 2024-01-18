import json
import logging
import logging.config
from collections import namedtuple
from datetime import datetime

import falcon

from api.config.config import get_logging_conf
from api.repository.models import Exercises, Food, Humor, Mood, Water
from api.resources.base import Resource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class MoodResource(Resource):
    """
    Manages Mood.

    `GET` /mood/{mood_id}
        Retrieves a single mood's data using its ID
    `GET` /mood/date/{mood_date}
        Retrieves all moods' data using the creation date
    `POST` /mood
        Adds a new mood entry with:
            exercises: data for exercises entry
            food_habits: data for food habits entry
            humors: data for humors entry
            water_intakes: data for water intakes entry
    `POST` /mood/date/{mood_date}
        Adds a new mood entry for a given date using pre-existing data for the date
    `PATCH` /mood/{mood_id}
        Updates a single mood's data using its ID
    `DELETE` /mood/{mood_id}
        Deletes a single mood's data using its ID
    `DELETE` /mood/date/{mood_date}
        Deletes all moods' data using the creation date
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
        """
        Retrieves a single mood's data using its ID

        `GET` /mood/{mood_id}

        Args:
            mood_id: the mood's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Mood's data successfully retrieved
        """
        simpleLogger.info(f"GET /mood/{mood_id}")
        user = self._get_user(req.context.get("username"))
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

        if user.id != mood.user_id:
            simpleLogger.debug(f"Invalid user for mood {mood_id}.")
            resp.text = json.dumps({"error": f"Invalid user for mood {mood_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        resp.text = json.dumps(mood.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /mood/{mood_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, mood_date: str):
        """
        Retrieves all moods' data using the creation date

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
        user = self._get_user(req.context.get("username"))
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

        all_moods = {
            mood.id: mood.as_dict() for mood in moods if mood.user_id == user.id
        }

        resp.text = json.dumps(all_moods)
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /mood/date/{mood_date} : successful")

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new mood entry

        `POST` /mood

        Required Body:
            `humors`: a Humor object
            `water_intakes`: a Water object.
            `exercises`: an Exercises object.
            `food_habits`: a Food object.

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: The server could not create a Mood instance

            `500 Server Error`: Database error

            `201 CREATED`: Mood's data successfully added
        """
        simpleLogger.info("POST /mood")
        user = self._get_user(req.context.get("username"))
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for mood.")
            resp.text = json.dumps({"error": "Missing request body for mood."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["date", "humors", "water_intakes", "exercises", "food_habits"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        params_classes = {
            "humors": Humor,
            "water_intakes": Water,
            "exercises": Exercises,
            "food_habits": Food,
        }

        try:
            mood_params = {
                key: [params_classes.get(key)(**body.get(key))]
                for key in ["humors", "water_intakes", "exercises", "food_habits"]
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
            mood = Mood(**mood_params, user_id=user.id)
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
            "humors": self.uow.repository.add_humor,
            "water_intakes": self.uow.repository.add_water_intake,
            "exercises": self.uow.repository.add_exercises,
            "food_habits": self.uow.repository.add_food_habits,
            "mood": self.uow.repository.add_mood,
        }

        for key in ["mood", "humors", "water_intakes", "exercises", "food_habits"]:
            try:
                simpleLogger.debug(
                    f"Trying to add {key.title().replace('_', ' ')} data to database."
                )
                if isinstance(mood_params[key], Mood):
                    params_db_functions[key](mood_params[key])
                else:
                    params_db_functions[key](mood_params[key].pop())
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

    def on_patch(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
        """
        Updates a single mood's data using its ID

        `PATCH` /mood/{mood_id}

        Args:
            mood_id: the mood's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Humor's data successfully updated
        """
        simpleLogger.info(f"PATCH /mood/{mood_id}")
        user = self._get_user(req.context.get("username"))
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

        if user.id != mood.user_id:
            simpleLogger.debug(f"Invalid user for mood {mood_id}.")
            resp.text = json.dumps({"error": f"Invalid user for mood {mood_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for mood.")
            resp.text = json.dumps({"error": "Missing request body for mood."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["humors", "water_intakes", "exercises", "food_habits"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for mood.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for mood."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        params_classes = {
            "humors": Humor,
            "water_intakes": Water,
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
                # TODO: Fix this trash
                corrected_key = key
                if key in ["humors", "water_intakes"]:
                    corrected_key = key[:-1]
                update_function = getattr(
                    self.uow.repository, f"update_{corrected_key}"
                )
                update_param = getattr(mood, key)
                simpleLogger.debug(
                    f"Updating {key.replace('_', ' ')} from database using id."
                )
                for param in update_param:
                    update_function(param, body[key])
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform update mood database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not update the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        updated_mood = self.uow.repository.get_mood_by_id(mood_id)
        resp.text = json.dumps(updated_mood.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"PATCH /mood/{mood_id} : successful")

    def on_delete(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
        """
        Deletes a single mood's data using its ID

        `DELETE` /mood/{mood_id}

        Args:
            mood_id: the mood's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Mood's data successfully deleted
        """
        simpleLogger.info(f"DELETE /mood/{mood_id}")
        user = self._get_user(req.context.get("username"))
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

        if user.id != mood.user_id:
            simpleLogger.debug(f"Invalid user for mood {mood_id}.")
            resp.text = json.dumps({"error": f"Invalid user for mood {mood_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
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
        Deletes all moods' data using the creation date

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
        user = self._get_user(req.context.get("username"))
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
                if user.id != mood.user_id:
                    simpleLogger.debug(f"Invalid user for mood {mood.id}.")
                    resp.text = json.dumps(
                        {"error": f"Invalid user for mood {mood.id}."}
                    )
                    resp.status = falcon.HTTP_FORBIDDEN
                    self.uow.rollback()
                    return
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
