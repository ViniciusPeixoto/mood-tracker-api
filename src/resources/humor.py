import json
import falcon
from datetime import datetime

from src.resources.base import Resource
from src.repository.models import Humor


class HumorResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, humor_id: int):
        humor = None
        try:
            humor = self.uow.repository.get_humor_by_id(humor_id)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not humor:
            resp.body = json.dumps({"error": f"No Humor data with id {humor_id}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.body = json.dumps(
            {
                "humor": {
                    "data": humor.date.strftime("%Y-%m-%d"),
                    "valor": humor.value,
                    "explicação": humor.description,
                    "saúde influenciou?": humor.health_based
                }
            }
        )
        resp.status = falcon.HTTP_OK

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, humor_date: str):
        humor = None
        try:
            humor_date = datetime.strptime(humor_date, "%Y-%m-%d").date()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            humor = self.uow.repository.get_humor_by_date(humor_date)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not humor:
            resp.body = json.dumps({"error": f"No Humor data in date {humor_date}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.body = json.dumps(
            {
                "humor": {
                    "data": humor.date.strftime("%Y-%m-%d"),
                    "valor": humor.value,
                    "explicação": humor.description,
                    "saúde influenciou?": humor.health_based
                }
            }
        )
        resp.status = falcon.HTTP_OK

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            resp.body = json.dumps({"error": "Missing request body."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        humor_value = body.get("value")
        humor_description = body.get("description")
        humor_health_based = body.get("health_based")

        if not all((humor_value, humor_description, humor_health_based)):
            resp.body = json.dumps({"error": "Missing Humor parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        humor = Humor(
            value=humor_value,
            description=humor_description,
            health_based=humor_health_based == "True"
        )
        try:
            self.uow.repository.add_mood(humor)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
