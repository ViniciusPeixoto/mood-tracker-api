import json
import logging
import logging.config
from datetime import datetime

import falcon
import jwt

from api.config.config import get_logging_conf, get_jwt_secret_key
from api.repository.models import User, UserAuth
from api.resources.base import Resource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class LoginResource(Resource):
    """
    login resource docstring
    """

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        """
        login post docstring
        """
        simpleLogger.info("POST /login")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for login.")
            resp.text = json.dumps({"error": "Missing request body for login."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["username", "password"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for login.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for login."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        user_auth = self.uow.repository.get_user_auth_by_username(body["username"])
        if not user_auth:
            simpleLogger.debug(f"No User data with username {body['username']}.")
            resp.text = json.dumps({"error": f"No User data with username {body['username']}."})
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if not body["password"] == user_auth.password:
            simpleLogger.debug(f"Invalid credentials for {user_auth.username}.")
            resp.text = json.dumps({"error": "Invalid credentials."})
            resp.status = falcon.HTTP_UNAUTHORIZED
            return

        token = jwt.encode({"username": user_auth.username}, get_jwt_secret_key(), algorithm="HS256")
        self.uow.repository.update_user_auth(user_auth, {"last_login": datetime.now()})
        resp.text = json.dumps({"token": token})
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"POST /login : successful")

    def on_post_register(self, req: falcon.Request, resp: falcon.Response):
        """
        register post docstring
        """
        simpleLogger.info("POST /register")
        body = req.stream.read(req.content_length or 0)
        body = json.loads(body.decode("utf-8"))
        if not body:
            simpleLogger.debug("Missing request body for register.")
            resp.text = json.dumps({"error": "Missing request body for register."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        allowed_params = ["username", "password"]
        if set(body.keys()).difference(allowed_params):
            simpleLogger.debug("Incorrect parameters in request body for register.")
            resp.text = json.dumps(
                {"error": "Incorrect parameters in request body for register."}
            )
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        try:
            user = User()
            user_auth = UserAuth(**body, user=user)
            self.uow.repository.add_user_auth(user_auth)
            self.uow.commit()
        except Exception:
            detailedLogger.error("Could not add new user to database.", exc_info=True)
            resp.text = json.dumps(
                {"error": "Could not add new user to database."}
            )
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"POST /login : successful")
