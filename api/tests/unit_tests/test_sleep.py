from datetime import date

import pytest
from sqlalchemy import select

from api.repository.models import Sleep
from api.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize(
    "sleep_id, status_code",
    [
        (11, 404),
        (1, 200),
    ],
)
def test_get(client, sleep_id, status_code, headers):
    result = client.simulate_get(f"/sleep/{sleep_id}", headers=headers)

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "sleep_date, status_code",
    [
        ("11-11-1111", 400),
        ("1111-11-11", 404),
        (str(date.today()), 200),
    ],
)
def test_get_from_date(client, sleep_date, status_code, headers):
    result = client.simulate_get(f"/sleep/date/{sleep_date}", headers=headers)

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        ({}, 400),
        (
            {
                "date": "2012-12-21",
                "value": 10,
                "minutes": 360,
                "description": "dreaming about stars",
                "extra": "this should break",
            },
            400,
        ),
        (
            {
                "date": "2012-12-21",
                "value": 10,
            },
            400,
        ),
        (
            {
                "date": "2012-12-21",
                "value": 10,
                "minutes": 360,
                "description": "dreaming about stars",
            },
            201,
        ),
    ],
)
def test_post(client, body, status_code, headers, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/sleep", json=body, headers=headers)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_sleep_by_date("2012-12-21").first()


@pytest.mark.parametrize(
    "body, status_code",
    [
        ({}, 400),
        (
            {
                "value": 10,
                "minutes": 360,
                "description": "dreaming of stars",
                "extra": "this should break",
            },
            400,
        ),
        (
            {
                "value": 10,
                "minutes": 360,
                "description": "dreaming of stars",
            },
            200,
        ),
        (
            {
                "value": 10,
            },
            200,
        ),
    ],
)
def test_update(client, body, status_code, headers, uow: AbstractUnitOfWork):
    sleep_params = {
        "date": "2012-12-21",
        "value": 1,
        "minutes": 10,
        "description": "Sleep for updating",
        "mood_id": 1,
    }
    sleep = Sleep(**sleep_params)
    sleep_id = None
    with uow:
        uow.repository.add_sleep(sleep)
        uow.flush()

        sleep_id = uow.repository.get_sleep_by_date("2012-12-21").first().id

        result = client.simulate_patch(f"/sleep/{sleep_id}", json=body, headers=headers)

    assert result.status_code == status_code

    if result.status_code < 400:
        sleep_params.update(body)
        with uow:
            assert uow.repository.get_sleep_by_date("2012-12-21").first() == Sleep(
                **sleep_params
            )


def test_delete(client, headers, uow: AbstractUnitOfWork):
    sleep = Sleep(
        date="2012-12-21",
        value="1",
        minutes=10,
        description="Sleep for deletion",
        mood_id=1,
    )
    sleep_id = None
    with uow:
        uow.repository.add_sleep(sleep)
        uow.flush()

        sleep_id = uow.repository.get_sleep_by_date("2012-12-21").first().id

        result = client.simulate_delete(f"/sleep/{sleep_id}", headers=headers)
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_sleep_by_id(sleep_id)


def test_delete_date(client, headers, uow: AbstractUnitOfWork):
    sleeps = [
        Sleep(
            date="2012-12-21",
            value="1",
            minutes=10,
            description="Sleep for deletion",
            mood_id=1,
        ),
        Sleep(
            date="2012-12-21",
            value="1",
            minutes=10,
            description="Sleep for deletion",
            mood_id=1,
        ),
    ]
    with uow:
        for sleep in sleeps:
            uow.repository.add_sleep(sleep)
        uow.flush()

        result = client.simulate_delete(f"/sleep/date/2012-12-21", headers=headers)
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_sleep_by_date("2012-12-21").first()
