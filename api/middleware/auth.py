import falcon
import jwt

from api.config.config import get_jwt_secret_key
from api.repository.unit_of_work import AbstractUnitOfWork

class AuthMiddleware:
    secret_key = get_jwt_secret_key()

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def process_request(self, req: falcon.Request, resp: falcon.Response):
        auth_header = req.get_header("Authorization")
        if not auth_header:
            raise falcon.HTTP_UNAUTHORIZED

        decoded = None
        try:
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise falcon.HTTPUnauthorized(description="Token expired.")
        except jwt.InvalidTokenError:
            raise falcon.HTTPUnauthorized(description="Invalid token.")

        username = decoded["username"]
        if not self.uow.repository.get_user_auth_by_username(username):
            raise falcon.HTTPUnauthorized(description="Invalid user.")

        req.context["user"] = username

