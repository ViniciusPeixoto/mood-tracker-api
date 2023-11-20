import json
from datetime import datetime

import falcon

from src.repository.models import Food
from src.resources.base import Resource


class FoodResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, food_id: int):
        food = None
        try:
            food = self.uow.repository.get_food_habits_by_id(food_id)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not food:
            resp.body = json.dumps({"error": f"No Food data with id {food_id}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(food)))
        resp.status = falcon.HTTP_OK

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, food_date: str):
        food = None
        try:
            food_date = datetime.strptime(food_date, "%Y-%m-%d").date()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            food = self.uow.repository.get_food_habits_by_date(food_date)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not food:
            resp.body = json.dumps({"error": f"No Food data in date {food_date}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(food)))
        resp.status = falcon.HTTP_OK

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            resp.body = json.dumps({"error": "Missing request body."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        food_value = body.get("value")
        food_description = body.get("description")

        if not all((food_value, food_description)):
            resp.body = json.dumps({"error": "Missing Food parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        food = Food(value=food_value, description=food_description)
        try:
            self.uow.repository.add_food_habits(food)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
