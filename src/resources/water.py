import json
import logging
import logging.config
from datetime import datetime

import falcon

from src.repository.models import Water
from src.resources.base import Resource


logging.config.fileConfig("src/utils/logging.conf")
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class WaterResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, water_intake_id: int):
        simpleLogger.info(f"GET /water-intake/{water_intake_id}")
        water_intake = None
        try:
            simpleLogger.debug("Fetching water intake from database using id.")
            water_intake = self.uow.repository.get_water_intake_by_id(water_intake_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform fetch water intake database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not fetch the water intake."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not water_intake:
            simpleLogger.debug(f"No Water data with id {water_intake_id}.")
            resp.body = json.dumps({"error": f"No Water data with id {water_intake_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(water_intake)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /water-intake/{water_intake_id} : successful")

    def on_get_date(
        self, req: falcon.Request, resp: falcon.Response, water_intake_date: str
    ):
        simpleLogger.info(f"GET /water-intake/date/{water_intake_date}")
        water_intake = None
        try:
            simpleLogger.debug("Formatting the date for water intake.")
            water_intake_date = datetime.strptime(water_intake_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {water_intake_date} is malformed!", exc_info=True)
            resp.body = json.dumps({"error": f"Date {water_intake_date} is malformed! Correct format is YYYY-MM-DD."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching water intake from database using date.")
            water_intake = self.uow.repository.get_water_intake_by_date(
                water_intake_date
            )
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform fetch water intake database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not fetch the water intake."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not water_intake:
            simpleLogger.debug(f"No Water data in date {water_intake_date}.")
            resp.body = json.dumps({"error": f"No Water data in date {water_intake_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(water_intake)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /water-intake/date/{water_intake_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        simpleLogger.info("POST /water-intake")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for water intake.")
            resp.body = json.dumps({"error": "Missing request body for water intake."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        water_intake_ml = body.get("milliliters")
        water_intake_description = body.get("description")
        water_intake_pee = body.get("pee")

        if not all((water_intake_ml, water_intake_description, water_intake_pee)):
            simpleLogger.debug("Missing Water parameter.")
            resp.body = json.dumps({"error": "Missing Water parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        water_intake = Water(
            milliliters=water_intake_ml,
            description=water_intake_description,
            pee=water_intake_pee == "True",
        )
        try:
            simpleLogger.debug("Trying to add Water data to database.")
            self.uow.repository.add_water_intake(water_intake)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform add water intake to database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not add the water intake."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /water-intake: successful")
