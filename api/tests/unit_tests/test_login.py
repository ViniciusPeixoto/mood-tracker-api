from datetime import datetime

import pytest

from api.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {},
            400,
        ),
        (
            {"user": "test_username", "pass": "test_password"},
            400,
        ),
        (
            {"username": "test_username1", "password": "test_password"},
            404,
        ),
        (
            {"username": "test_username", "password": "test_password1"},
            401,
        ),
        (
            {"username": "test_username", "password": "test_password"},
            200,
        ),
    ],
)
def test_post_login(client, body, status_code):
    result = client.simulate_post(f"/login", json=body)

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {},
            400,
        ),
        (
            {"user": "test_username", "pass": "test_password"},
            400,
        ),
        (
            {"username": "test_username", "password": "test_password"},
            403,
        ),
        (
            {"username": "test_new_username", "password": "test_new_password"},
            204,
        ),
    ],
)
def test_post_register(client, body, status_code, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/register", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            user_auth = uow.repository.get_user_auth_by_username(body.get("username"))
            assert user_auth.username == body.get("username")
            assert user_auth.password == body.get("password")
            assert user_auth.active is True
            assert len(user_auth.token) == 0
            assert user_auth.created_at == datetime.today().date()
