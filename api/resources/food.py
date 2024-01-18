import json
import logging
import logging.config
from datetime import datetime

import falcon

from api.config.config import get_logging_conf
from api.repository.models import Food
from api.resources.base import Resource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class FoodResource(Resource):
    """
    Manages Food Habits.

    `GET` /food/{food_id}
        Retrieves a single food habit's data using its ID
    `GET` /food/date/{food_date}
        Retrieves all food habits' data using the creation date
    `POST` /food
        Adds a new food habit entry with:
            value: evaluation of food habit
            description: text describing the given grade
    `PATCH` /food/{food_id}
        Updates a single food habit's data using its ID
    `DELETE` /food/{food_id}
        Deletes a single food habit's data using its ID
    `DELETE` /food/date/{food_date}
        Deletes all food habits' data using the creation date
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, food_id: int):
        """
        Retrieves a single food habit's data using its ID

        `GET` /food/{food_id}

        Args:
            food_id: the food habit's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Food habit's data successfully retrieved
        """
        simpleLogger.info(f"GET /food/{food_id}")
        user = self._get_user(req.context.get("username"))
        food = None

        try:
            simpleLogger.debug("Fetching food habits from database using id.")
            food = self.uow.repository.get_food_habits_by_id(food_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch food habits database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the food habit."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not food:
            simpleLogger.debug(f"No Food data with id {food_id}.")
            resp.text = json.dumps({"error": f"No Food data with id {food_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != food.mood.user_id:
            simpleLogger.debug(f"Invalid user for food {food_id}.")
            resp.text = json.dumps({"error": f"Invalid user for food {food_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        resp.text = json.dumps(food.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /food/{food_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, food_date: str):
        """
        Retrieves all food habits' data using the creation date

        `GET` /food/date/{food_date}

        Args:
            food_date: the food habits' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Food habits' data successfully retrieved
        """
        simpleLogger.info(f"GET /food/date/{food_date}")
        user = self._get_user(req.context.get("username"))
        foods = None

        try:
            simpleLogger.debug("Formatting the date for food.")
            food_date = datetime.strptime(food_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {food_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {food_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching food habits from database using date.")
            foods = self.uow.repository.get_food_habits_by_date(food_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch foods database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the food."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not foods.first():
            simpleLogger.debug(f"No Food data in date {food_date}.")
            resp.text = json.dumps({"error": f"No Food data in date {food_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        all_foods = {
            food.id: food.as_dict() for food in foods if food.mood.user_id == user.id
        }

        resp.text = json.dumps(all_foods)
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /food/date/{food_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new food habit entry

        `POST` /food

        Required Body:
            `value`: evaluation of food habit
            `description`: text describing the given grade

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: Database error

            `201 CREATED`: Food habit's data successfully added
        """
        simpleLogger.info("POST /food")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for food habits.")
            resp.text = json.dumps({"error": "Missing request body for food habits."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["date", "value", "description"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for food.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for food."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        if not all(key in body for key in ["value", "description"]):
            simpleLogger.debug("Missing Food parameter.")
            resp.text = json.dumps({"error": "Missing Food parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        food_date = body.get("date") or str(datetime.today().date())
        user = self._get_user(req.context.get("username"))
        mood = self._get_mood_from_date(food_date, user.id)

        try:
            food = Food(**body, mood_id=mood.id)
        except Exception as e:
            detailedLogger.error("Could not create a Food instance!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": "The server could not create a Food with the parameters provided."
                }
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        try:
            simpleLogger.debug("Trying to add Food data to database.")
            self.uow.repository.add_food_habits(food)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add food habits to database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not add the food habit."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /food : successful")

    def on_patch(self, req: falcon.Request, resp: falcon.Response, food_id: int):
        """
        Updates a single food habit's data using its ID

        `PATCH` /food/{food_id}

        Args:
            food_id: the food habits's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Food's data successfully updated
        """
        simpleLogger.info(f"PATCH /food/{food_id}")
        user = self._get_user(req.context.get("username"))
        food_habits = None

        try:
            simpleLogger.debug("Fetching food habits from database using id.")
            food_habits = self.uow.repository.get_food_habits_by_id(food_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch food habits database operation!", exc_info=True
            )
            resp.text = json.dumps(
                {"error": "The server could not fetch the food habits."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not food_habits:
            simpleLogger.debug(f"No Food Habits data with id {food_id}.")
            resp.text = json.dumps({"error": f"No Food Habits data with id {food_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != food_habits.mood.user_id:
            simpleLogger.debug(f"Invalid user for food {food_id}.")
            resp.text = json.dumps({"error": f"Invalid user for food {food_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for food habits.")
            resp.text = json.dumps({"error": "Missing request body for food habits."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["value", "description"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for food.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for food."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Updating food habits from database using id.")
            self.uow.repository.update_food_habits(food_habits, body)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform update food habits database operation!",
                exc_info=True,
            )
            resp.text = json.dumps(
                {"error": "The server could not update the food habits."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        updated_food = self.uow.repository.get_food_habits_by_id(food_id)
        resp.text = json.dumps(updated_food.as_dict())
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"PATCH /food/{food_id} : successful")

    def on_delete(self, req: falcon.Request, resp: falcon.Response, food_id: int):
        """
        Deletes a single food habit's data using its ID

        `DELETE` /food/{food_id}

        Args:
            food_id: the food's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `204 No Content`: Food's data successfully deleted
        """
        simpleLogger.info(f"DELETE /food/{food_id}")
        user = self._get_user(req.context.get("username"))
        food = None

        try:
            simpleLogger.debug("Fetching food from database using id.")
            food = self.uow.repository.get_food_habits_by_id(food_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch food database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the food."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not food:
            simpleLogger.debug(f"No Food data with id {food_id}.")
            resp.text = json.dumps({"error": f"No Food data with id {food_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if user.id != food.mood.user_id:
            simpleLogger.debug(f"Invalid user for food {food_id}.")
            resp.text = json.dumps({"error": f"Invalid user for food {food_id}."})
            resp.status = falcon.HTTP_FORBIDDEN
            return

        try:
            simpleLogger.debug("Deleting food from database using id.")
            self.uow.repository.delete_food_habits(food)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete food database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the food."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /food/{food_id} : successful")

    def on_delete_date(
        self, req: falcon.Request, resp: falcon.Response, food_date: str
    ):
        """
        Deletes all food habits' data using the creation date

        `DELETE` /food/date/{food_date}

        Args:
            food_date: the food habits' creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `204 No Content`: Foods' data successfully deleted
        """
        simpleLogger.info(f"DELETE /food/date/{food_date}")
        user = self._get_user(req.context.get("username"))
        foods = None

        try:
            simpleLogger.debug("Formatting the date for food.")
            food_date = datetime.strptime(food_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {food_date} is malformed!", exc_info=True)
            resp.text = json.dumps(
                {
                    "error": f"Date {food_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            simpleLogger.debug("Fetching foods from database using date.")
            foods = self.uow.repository.get_food_habits_by_date(food_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch food database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not fetch the food."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not foods.first():
            simpleLogger.debug(f"No Food data in date {food_date}.")
            resp.text = json.dumps({"error": f"No Food data in date {food_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        try:
            simpleLogger.debug("Deleting foods from database using date.")
            for food in foods:
                if user.id != food.mood.user_id:
                    simpleLogger.debug(f"Invalid user for food {food.id}.")
                    resp.text = json.dumps(
                        {"error": f"Invalid user for food {food.id}."}
                    )
                    resp.status = falcon.HTTP_FORBIDDEN
                    self.uow.rollback()
                    return
                self.uow.repository.delete_food_habits(food)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform delete foods database operation!", exc_info=True
            )
            resp.text = json.dumps({"error": "The server could not delete the foods."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"DELETE /food/date/{food_date} : successful")
