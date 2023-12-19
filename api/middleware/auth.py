import logging
import logging.config
from datetime import datetime, timedelta

import falcon
import jwt

from api.config.config import get_logging_conf, get_jwt_secret_key
from api.repository.unit_of_work import AbstractUnitOfWork
from api.resources.base import Resource


logging.config.fileConfig(get_logging_conf())
simpleLogger = logging.getLogger("simpleLogger")
detailedLogger = logging.getLogger("detailedLogger")


class AuthMiddleware:
    secret_key = get_jwt_secret_key()
    ignore_paths = ["/login", "/register"]

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def process_request(self, req: falcon.Request, resp: falcon.Response):
        if req.path in self.ignore_paths:
            return

        username = req.get_header("username")
        if not username:
            raise falcon.HTTPUnauthorized("No USERNAME header.")

        user_auth = self.uow.repository.get_user_auth_by_username(username)
        if not user_auth:
            raise falcon.HTTPUnauthorized(description="Invalid user.")

        try:
            decoded = jwt.decode(user_auth.token, self.secret_key, algorithms=["HS256"])
        except IndexError:
            raise falcon.HTTPUnauthorized(description="Token malformed.")
        except jwt.ExpiredSignatureError:
            raise falcon.HTTPUnauthorized(description="Token expired.")
        except jwt.InvalidTokenError:
            raise falcon.HTTPUnauthorized(description="Invalid token.")

        req.context["username"] = username

    def process_response(self, req: falcon.Request, resp: falcon.Response, resource: Resource, req_succeeded: bool) -> None:
        if req.path in self.ignore_paths:
            return

        user_auth = self.uow.repository.get_user_auth_by_username(req.context.get("username"))
        if not user_auth:
            return

        refresh_data = {
            "exp": str(int((datetime.now() + timedelta(minutes=5)).timestamp())),
            "user_auth_id": str(user_auth.id),
            "user_auth_username": str(user_auth.username),
            "user_auth_user_id": str(user_auth.user_id),
            "user_auth_last_login": str(user_auth.last_login),
        }
        token = jwt.encode(refresh_data, self.secret_key, algorithm="HS256")
        try:
            self.uow.repository.update_user_auth(user_auth, {"token": token})
            self.uow.commit()
        except Exception as e:
            detailedLogger.error("Could not refresh token to user_auth.", exc_info=True)
            raise e

