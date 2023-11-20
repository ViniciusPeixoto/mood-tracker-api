import json
from datetime import datetime

import falcon

from src.repository.models import Exercises, Food, Humor, Mood, Water
from src.resources.base import Resource


class MoodResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, mood_id: int):
        mood = None
        try:
            mood = self.uow.repository.get_mood_by_id(mood_id)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not mood:
            resp.body = json.dumps({"error": f"No Mood data with id {mood_id}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(mood)))
        resp.status = falcon.HTTP_OK

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, mood_date: str):
        mood = None
        try:
            mood_date = datetime.strptime(mood_date, "%Y-%m-%d").date()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            mood = self.uow.repository.get_mood_by_date(mood_date)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not mood:
            resp.body = json.dumps({"error": f"No Mood data in date {mood_date}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(mood)))
        resp.status = falcon.HTTP_OK

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            resp.body = json.dumps({"error": "Missing request body."})
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
            mood = Mood(**mood_params)
        except TypeError as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        try:
            self.uow.repository.add_mood(mood)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED

    def on_post_date(self, req: falcon.Request, resp: falcon.Response, mood_date: str):
        try:
            mood_date = datetime.strptime(mood_date, "%Y-%m-%d").date()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        mood = self.build_mood(date=mood_date)

        try:
            self.uow.repository.add_mood(mood)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED

    def build_mood(self, date: datetime) -> Mood:
        mood_params = {"date": date}
        for param in ["humor", "water_intake", "exercises", "food_habits"]:
            function_name = f"get_{param}_by_date"
            db_function = getattr(self.uow.repository, function_name)
            mood_params[param] = db_function(date)

        return Mood(**mood_params)
