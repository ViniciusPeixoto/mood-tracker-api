import json
import falcon
from datetime import datetime

from src.resources.base import Resource
from src.repository.models import Water


class WaterResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, water_intake_id: int):
        water_intake = None
        try:
            water_intake = self.uow.repository.get_water_intake_by_id(water_intake_id)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not water_intake:
            resp.body = json.dumps({"error": f"No Water Intake data with id {water_intake_id}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(water_intake)))
        resp.status = falcon.HTTP_OK

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, water_intake_date: str):
        water_intake = None
        try:
            water_intake_date = datetime.strptime(water_intake_date, "%Y-%m-%d").date()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            water_intake = self.uow.repository.get_water_intake_by_date(water_intake_date)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not water_intake:
            resp.body = json.dumps({"error": f"No Water Intake data in date {water_intake_date}"})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(water_intake)))
        resp.status = falcon.HTTP_OK

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            resp.body = json.dumps({"error": "Missing request body."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        water_intake_ml = body.get("milliliters")
        water_intake_description = body.get("description")
        water_intake_pee = body.get("pee")

        if not all((water_intake_ml, water_intake_description, water_intake_pee)):
            resp.body = json.dumps({"error": "Missing Water Intake parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        water_intake = Water(
            milliliters=water_intake_ml,
            description=water_intake_description,
            pee=water_intake_pee == "True"
        )
        try:
            self.uow.repository.add_water_intake(water_intake)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
