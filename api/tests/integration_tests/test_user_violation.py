from datetime import date

import pytest
import jwt

from api.config.config import get_jwt_secret_key
from api.repository.models import User, UserAuth
from api.repository.unit_of_work import AbstractUnitOfWork


def create_access_token(username: str) -> str:
    secret_key = get_jwt_secret_key()
    data = {"user_auth_username": username}
    token = jwt.encode(data, secret_key, algorithm="HS256")
    return token


def test_user_cannot_access_items_from_another_user(client, uow: AbstractUnitOfWork):
    today = date.today()
    token = create_access_token("new_username")

    with uow:
        uow.repository.add_user(User())
        uow.repository.add_user(UserAuth(username="new_username", password="new_password", created_at=today, last_login=today, token=token, user_id=2))
        uow.commit()

    headers = {"Authorization": f"Bearer: {token}"}
    for endpoint in ["/exercises", "/food", "/humor", "/mood", "/water-intake"]:
        result = client.simulate_get(f"{endpoint}/1", headers=headers)
        assert result.status_code == 403

        result = client.simulate_patch(f"{endpoint}/1", json={}, headers=headers)
        assert result.status_code == 403

        result = client.simulate_delete(f"{endpoint}/1", headers=headers)
        assert result.status_code == 403

        result = client.simulate_delete(f"{endpoint}/date/{str(today)}", headers=headers)
        assert result.status_code == 403
