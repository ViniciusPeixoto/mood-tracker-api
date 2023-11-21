import json
import logging
import logging.config
from datetime import datetime

import falcon

from src.repository.models import Exercises, Food, Humor, Mood, Water
from src.resources.base import Resource

logging.config.fileConfig("src/utils/logging.conf")
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class MoodResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
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
            resp.body = json.dumps({"error": "The server could not fetch the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not mood:
            simpleLogger.debug(f"No Mood data with id {mood_id}.")
            resp.body = json.dumps({"error": f"No Mood data with id {mood_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(mood)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /mood/{mood_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, mood_date: str):
        simpleLogger.info(f"GET /mood/date/{mood_date}")
        mood = None
        try:
            simpleLogger.debug("Formatting the date for mood.")
            mood_date = datetime.strptime(mood_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {mood_date} is malformed!", exc_info=True)
            resp.body = json.dumps(
                {
                    "error": f"Date {mood_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching mood from database using date.")
            mood = self.uow.repository.get_mood_by_date(mood_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch mood database operation!", exc_info=True
            )
            resp.body = json.dumps({"error": "The server could not fetch the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not mood:
            simpleLogger.debug(f"No Mood data in date {mood_date}.")
            resp.body = json.dumps({"error": f"No Mood data in date {mood_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(mood)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /mood/date/{mood_date} : successful")

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        simpleLogger.info("POST /mood")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for mood.")
            resp.body = json.dumps({"error": "Missing request body for mood."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        params_classes = {
            "humor": Humor,
            "water_intake": Water,
            "exercises": Exercises,
            "food_habits": Food,
        }
        mood_params = {
            key: params_classes.get(key)(**body.get(key))
            for key in ["humor", "water_intake", "exercises", "food_habits"]
        }
        try:
            simpleLogger.debug("Trying to create a Mood instance.")
            mood = Mood(**mood_params)
        except TypeError as e:
            detailedLogger.error("Could not create a Mood instance!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not create a Mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        try:
            simpleLogger.debug("Trying to add Mood data to database.")
            self.uow.repository.add_mood(mood)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add mood to database operation!", exc_info=True
            )
            resp.body = json.dumps({"error": "The server could not add the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /mood : successful")

    def on_post_date(self, req: falcon.Request, resp: falcon.Response, mood_date: str):
        simpleLogger.info(f"POST /mood/date/{mood_date}")
        try:
            simpleLogger.debug("Formatting the date for post mood.")
            mood_date = datetime.strptime(mood_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {mood_date} is malformed!", exc_info=True)
            resp.body = json.dumps(
                {
                    "error": f"Date {mood_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Building a Mood instance from multiple dates.")
            mood = self.build_mood(date=mood_date)
        except Exception as e:
            detailedLogger.error("Could not build Mood.", exc_info=True)
            resp.body = json.dumps(
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
            resp.body = json.dumps({"error": "The server could not add the mood."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info(f"POST /mood/date/{mood_date}")

    def build_mood(self, date: datetime) -> Mood:
        simpleLogger.info(f"Building Mood with data from {date}")
        mood_params = {"date": date}
        for param in ["humor", "water_intake", "exercises", "food_habits"]:
            function_name = f"get_{param}_by_date"
            db_function = getattr(self.uow.repository, function_name)
            mood_params[param] = db_function(date)

        return Mood(**mood_params)
