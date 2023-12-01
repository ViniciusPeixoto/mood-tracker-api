from datetime import date

import pytest
from sqlalchemy import select

from src.repository.models import Humor
from src.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("humor_id, status_code", [(1, 200), (11, 404)])
def test_get(client, humor_id, status_code):
    result = client.simulate_get(f"/humor/{humor_id}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "humor_date, status_code",
    [
        (str(date.today()), 200),
        ("1111-11-11", 404),
        ("11-11-1111", 400),
    ],
)
def test_get_from_date(client, humor_date, status_code):
    result = client.simulate_get(f"/humor/date/{humor_date}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
                "date": "2012-12-21",
                "value": 10,
                "description": "smiling in the park",
                "health_based": False,
            },
            201,
        ),
        (
            {
                "date": "2012-12-21",
                "value": 10,
            },
            400,
        ),
        ({}, 400),
        (
            {
                "date": "2012-12-21",
                "value": 10,
                "description": "smiling in the park",
                "health_based": False,
                "extra": "this should break",
            },
            400,
        ),
    ],
)
def test_post(client, body, status_code, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/humor", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_humor_by_date("2012-12-21")


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
                "value": 10,
                "description": "smiling in the park",
                "health_based": False,
            },
            200,
        ),
        (
            {
                "value": 10,
            },
            200,
        ),
        ({}, 400),
        (
            {
                "value": 10,
                "description": "smiling in the park",
                "health_based": False,
                "extra": "this should break",
            },
            400,
        ),
    ],
)
def test_update(client, body, status_code, uow: AbstractUnitOfWork):
    humor_params = {"date":"2012-12-21",
        "value":"1",
        "description":"Humor for updating",
        "health_based":True}
    humor = Humor(**humor_params)
    humor_id = None
    with uow:
        uow.repository.add_humor(humor)
        uow.flush()

        humor_id = uow.repository.get_humor_by_date("2012-12-21").id

        result = client.simulate_patch(f"/humor/{humor_id}", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        humor_params.update(body)
        with uow:
            assert uow.repository.get_humor_by_date("2012-12-21") == Humor(**humor_params)


def test_delete(client, uow: AbstractUnitOfWork):
    humor = Humor(
        date="2012-12-21",
        value="1",
        description="Humor for deletion",
        health_based=True,
    )
    humor_id = None
    with uow:
        uow.repository.add_humor(humor)
        uow.flush()

        humor_id = uow.repository.get_humor_by_date("2012-12-21").id

        result = client.simulate_delete(f"/humor/{humor_id}")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_humor_by_id(humor_id)
