import json
from datetime import datetime

import falcon

from src.repository.models import Exercises
from src.resources.base import Resource


class ExercisesResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, exercises_id: int):
        exercises = None
        try:
            exercises = self.uow.repository.get_exercises_by_id(exercises_id)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not exercises:
            resp.body = json.dumps(
                {"error": f"No Exercises data with id {exercises_id}"}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(exercises)))
        resp.status = falcon.HTTP_OK

    def on_get_date(
        self, req: falcon.Request, resp: falcon.Response, exercises_date: str
    ):
        exercises = None
        try:
            exercises_date = datetime.strptime(exercises_date, "%Y-%m-%d").date()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            exercises = self.uow.repository.get_exercises_by_date(exercises_date)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not exercises:
            resp.body = json.dumps(
                {"error": f"No Exercises data in date {exercises_date}"}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(exercises)))
        resp.status = falcon.HTTP_OK

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            resp.body = json.dumps({"error": "Missing request body."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        exercises_minutes = body.get("minutes")
        exercises_description = body.get("description")

        if not all((exercises_minutes, exercises_description)):
            resp.body = json.dumps({"error": "Missing Exercises parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        exercises = Exercises(
            minutes=exercises_minutes, description=exercises_description
        )
        try:
            self.uow.repository.add_exercises(exercises)
            self.uow.commit()
        except Exception as e:
            resp.body = json.dumps({"exception": e.__str__()})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
