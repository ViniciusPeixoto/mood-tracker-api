import json
import logging
import logging.config
from datetime import datetime

import falcon

from src.repository.models import Food
from src.resources.base import Resource

logging.config.fileConfig("src/utils/logging.conf")
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class FoodResource(Resource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, food_id: int):
        simpleLogger.info(f"GET /food/{food_id}")
        food = None
        try:
            simpleLogger.debug("Fetching food habits from database using id.")
            food = self.uow.repository.get_food_habits_by_id(food_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform fetch food habits database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not fetch the food habit."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not food:
            simpleLogger.debug(f"No Food data with id {food_id}.")
            resp.body = json.dumps({"error": f"No Food data with id {food_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(food)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /food/{food_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, food_date: str):
        simpleLogger.info(f"GET /food/date/{food_date}")
        food = None
        try:
            simpleLogger.debug("Formatting the date for food.")
            food_date = datetime.strptime(food_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {food_date} is malformed!", exc_info=True)
            resp.body = json.dumps({"error": f"Date {food_date} is malformed! Correct format is YYYY-MM-DD."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching food habits from database using date.")
            food = self.uow.repository.get_food_habits_by_date(food_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform fetch food database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not fetch the food."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not food:
            simpleLogger.debug(f"No Food data in date {food_date}.")
            resp.body = json.dumps({"error": f"No Food data in date {food_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(food)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /food/date/{food_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        simpleLogger.info("POST /food")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for food habits.")
            resp.body = json.dumps({"error": "Missing request body for food habits."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        food_value = body.get("value")
        food_description = body.get("description")

        if not all((food_value, food_description)):
            simpleLogger.debug("Missing Food parameter.")
            resp.body = json.dumps({"error": "Missing Food parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        food = Food(value=food_value, description=food_description)
        try:
            simpleLogger.debug("Trying to add Food data to database.")
            self.uow.repository.add_food_habits(food)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not perform add food habits to database operation!", exc_info=True)
            resp.body = json.dumps({"error": "The server could not add the food habit."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /food : successful")
