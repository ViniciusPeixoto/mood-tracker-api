import json
import logging
import logging.config
from datetime import datetime

import falcon

from src.repository.models import Humor
from src.resources.base import Resource

logging.config.fileConfig("src/utils/logging.conf")
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class HumorResource(Resource):
    """
    Manages Humor.

    `GET` /humor/{humor_id}
        Retrieves a single humor's data using its ID
    `GET` /humor/date/{humor_date}
        Retrieves a single humor's data using its creation date
    `POST` /humor
        Adds a new humor entry with:
            value: evaluation of humor
            description: text describing the given grade
            health_based: True/False if health issues influenced the given grade
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response, humor_id: int):
        """
        Retrieves a single humor's data using humor's ID

        `GET` /humor/{humor_id}

        Args:
            humor_id: the humor's ID

        Responses:
            `404 Not Found`: No data for given ID

            `500 Server Error`: Database error

            `200 OK`: Humor's data successfully retrieved
        """
        simpleLogger.info(f"GET /humor/{humor_id}")
        humor = None
        try:
            simpleLogger.debug("Fetching humor from database using id.")
            humor = self.uow.repository.get_humor_by_id(humor_id)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch humor database operation!", exc_info=True
            )
            resp.body = json.dumps({"error": "The server could not fetch the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR

        if not humor:
            simpleLogger.debug(f"No Humor data with id {humor_id}.")
            resp.body = json.dumps({"error": f"No Humor data with id {humor_id}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(humor)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /humor/{humor_id} : successful")

    def on_get_date(self, req: falcon.Request, resp: falcon.Response, humor_date: str):
        """
        Retrieves a single humor's data using humor's creation date

        `GET` /humor/date/{humor_date}

        Args:
            humor_date: the humor's creation date

        Responses:
            `400 Bad Request`: Date could not be parsed

            `404 Not Found`: No data for given date

            `500 Server Error`: Database error

            `200 OK`: Humor's data successfully retrieved
        """
        simpleLogger.info(f"GET /humor/date/{humor_date}")
        humor = None
        try:
            simpleLogger.debug("Formatting the date for humor.")
            humor_date = datetime.strptime(humor_date, "%Y-%m-%d").date()
        except Exception as e:
            detailedLogger.warning(f"Date {humor_date} is malformed!", exc_info=True)
            resp.body = json.dumps(
                {
                    "error": f"Date {humor_date} is malformed! Correct format is YYYY-MM-DD."
                }
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        try:
            simpleLogger.debug("Fetching humor from database using date.")
            humor = self.uow.repository.get_humor_by_date(humor_date)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform fetch humor database operation!", exc_info=True
            )
            resp.body = json.dumps({"error": "The server could not fetch the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        if not humor:
            simpleLogger.debug(f"No Humor data in date {humor_date}.")
            resp.body = json.dumps({"error": f"No Humor data in date {humor_date}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        resp.text = json.dumps(json.loads(str(humor)))
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"GET /humor/date/{humor_date} : successful")

    def on_post_add(self, req: falcon.Request, resp: falcon.Response):
        """
        Adds a new humor

        `POST` /humor

        Required Body:
            `value`: evaluation of humor
            `description`: text describing the given grade
            `health_based`: True/False if health issues influenced the given grade

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: Database error
            
            `201 CREATED`: Humor's data successfully added
        """
        simpleLogger.info("POST /humor")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for humor.")
            resp.body = json.dumps({"error": "Missing request body for humor."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        humor_value = body.get("value")
        humor_description = body.get("description")
        humor_health_based = body.get("health_based")

        if not all((humor_value, humor_description, humor_health_based)):
            simpleLogger.debug("Missing Humor parameter.")
            resp.body = json.dumps({"error": "Missing Humor parameter."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        humor = Humor(
            value=humor_value,
            description=humor_description,
            health_based=humor_health_based == "True",
        )
        try:
            simpleLogger.debug("Trying to add Humor data to database.")
            self.uow.repository.add_humor(humor)
            self.uow.commit()
        except Exception as e:
            detailedLogger.error(
                "Could not perform add humor to database operation!", exc_info=True
            )
            resp.body = json.dumps({"error": "The server could not add the humor."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_CREATED
        simpleLogger.info("POST /humor : successful")
