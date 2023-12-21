import json
import logging
import logging.config
from datetime import datetime, timedelta

import falcon
import jwt
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from api.config.config import AUTHENTICATION_TTL, get_jwt_secret_key, get_logging_conf
from api.repository.models import User, UserAuth
from api.resources.base import Resource

logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class LoginResource(Resource):
    """
    Manages Login and Registration.

    `POST` /login
        Validates credentials for authentication:
            username: user's username
            password: user's password
    `POST` /register
        Creates a new user with credentials:
            username: user's username
            password: user's password
    """

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        """
        Validates credentials for authentication

        `POST` /login

        Required Body:
            `username`: user's username
            `password`: user's password

        Responses:
            `400 Bad Request`: Body data is missing

            `401 Unauthorized`: Invalid credentials for user

            `404 Not Found`: No User data with username

            `500 Server Error`: Database error

            `204 No Content`: User's data successfully validated
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

        user_auth = self.uow.repository.get_user_auth_by_username(body.get("username"))
        if not user_auth:
            simpleLogger.debug(f"No User data with username {body.get('username')}.")
            resp.text = json.dumps(
                {"error": f"No User data with username {body.get('username')}."}
            )
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if not body.get("password") == user_auth.password:
            simpleLogger.debug(f"Invalid credentials for {user_auth.username}.")
            resp.text = json.dumps({"error": "Invalid credentials."})
            resp.status = falcon.HTTP_UNAUTHORIZED
            return

        self.uow.repository.update_user_auth(user_auth, {"last_login": datetime.now()})
        login_data = {
            "exp": str(
                int(
                    (datetime.now() + timedelta(minutes=AUTHENTICATION_TTL)).timestamp()
                )
            ),
            "user_auth_id": str(user_auth.id),
            "user_auth_username": str(user_auth.username),
            "user_auth_user_id": str(user_auth.user_id),
            "user_auth_last_login": str(user_auth.last_login),
        }
        token = jwt.encode(login_data, get_jwt_secret_key(), algorithm="HS256")

        try:
            self.uow.repository.update_user_auth(user_auth, {"token": token})
            self.uow.commit()
        except Exception:
            detailedLogger.error("Could not add token to user_auth.", exc_info=True)
            resp.text = json.dumps({"error": "Could not add token to user_auth."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.text = json.dumps({"token": token})
        resp.status = falcon.HTTP_OK
        simpleLogger.info(f"POST /login : successful")

    def on_post_register(self, req: falcon.Request, resp: falcon.Response):
        """
        Creates a new user with credentials

        `POST` /register

        Required Body:
            `username`: user's username
            `password`: user's password

        Responses:
            `400 Bad Request`: Body data is missing

            `500 Server Error`: Database error

            `204 No Content`: User's data successfully created
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
            user_auth = UserAuth(**body, user=user, token="")
            self.uow.repository.add_user_auth(user_auth)
            self.uow.commit()
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                detailedLogger.error("Username already exists.", exc_info=True)
                resp.text = json.dumps({"error": "Username already exists."})
                resp.status = falcon.HTTP_FORBIDDEN
                return
            detailedLogger.error("Could not add new user to database.", exc_info=True)
            resp.text = json.dumps({"error": "Could not add new user to database."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return
        except Exception:
            detailedLogger.error("Could not add new user to database.", exc_info=True)
            resp.text = json.dumps({"error": "Could not add new user to database."})
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            return

        resp.status = falcon.HTTP_NO_CONTENT
        simpleLogger.info(f"POST /login : successful")
