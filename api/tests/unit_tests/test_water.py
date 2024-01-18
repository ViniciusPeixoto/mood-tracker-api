from datetime import date

import pytest
from sqlalchemy import select

from api.repository.models import Water
from api.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize(
    "water_id, status_code",
    [
        (11, 404),
        (1, 200),
    ],
)
def test_get(client, water_id, status_code, headers):
    result = client.simulate_get(f"/water-intake/{water_id}", headers=headers)

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "water_date, status_code",
    [
        ("11-11-1111", 400),
        ("1111-11-11", 404),
        (str(date.today()), 200),
    ],
)
def test_get_from_date(client, water_date, status_code, headers):
    result = client.simulate_get(f"/water-intake/date/{water_date}", headers=headers)

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        ({}, 400),
        (
            {
                "date": "2012-12-21",
                "milliliters": 1000,
                "description": "drinking in the park",
                "pee": False,
                "extra": "this should break",
            },
            400,
        ),
        (
            {
                "date": "2012-12-21",
                "milliliters": 1000,
            },
            400,
        ),
        (
            {
                "date": "2012-12-21",
                "milliliters": 1000,
                "description": "drinking in the park",
                "pee": False,
            },
            201,
        ),
    ],
)
def test_post(client, body, status_code, headers, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/water-intake", json=body, headers=headers)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_water_intake_by_date("2012-12-21").first()


@pytest.mark.parametrize(
    "body, status_code",
    [
        ({}, 400),
        (
            {
                "milliliters": 10,
                "description": "eating in the park",
                "pee": False,
                "extra": "this should break",
            },
            400,
        ),
        (
            {"milliliters": 10, "description": "eating in the park", "pee": False},
            200,
        ),
        (
            {
                "milliliters": 10,
            },
            200,
        ),
    ],
)
def test_update(client, body, status_code, headers, uow: AbstractUnitOfWork):
    water_intake_params = {
        "date": "2012-12-21",
        "milliliters": "1",
        "description": "Water for updating",
        "pee": True,
        "mood_id": 1,
    }
    water_intake = Water(**water_intake_params)
    water_intake_id = None

    with uow:
        uow.repository.add_water_intake(water_intake)
        uow.flush()

        water_intake_id = (
            uow.repository.get_water_intake_by_date("2012-12-21").first().id
        )

        result = client.simulate_patch(
            f"/water-intake/{water_intake_id}", json=body, headers=headers
        )

    assert result.status_code == status_code

    if result.status_code < 400:
        water_intake_params.update(body)
        with uow:
            assert uow.repository.get_water_intake_by_date(
                "2012-12-21"
            ).first() == Water(**water_intake_params)


def test_delete(client, headers, uow: AbstractUnitOfWork):
    water_intake = Water(
        date="2012-12-21",
        milliliters="1",
        description="Water Intake for deletion",
        pee=True,
        mood_id=1,
    )
    water_intake_id = None

    with uow:
        uow.repository.add_water_intake(water_intake)
        uow.flush()

        water_intake_id = (
            uow.repository.get_water_intake_by_date("2012-12-21").first().id
        )

        result = client.simulate_delete(
            f"/water-intake/{water_intake_id}", headers=headers
        )
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_water_intake_by_id(water_intake_id)


def test_delete_date(client, headers, uow: AbstractUnitOfWork):
    water_intakes = [
        Water(
            date="2012-12-21",
            milliliters="1",
            description="Water Intake for deletion",
            pee=True,
            mood_id=1,
        ),
        Water(
            date="2012-12-21",
            milliliters="1",
            description="Water Intake for deletion",
            pee=True,
            mood_id=1,
        ),
    ]

    with uow:
        for water_intake in water_intakes:
            uow.repository.add_water_intake(water_intake)
        uow.flush()

        result = client.simulate_delete(
            f"/water-intake/date/2012-12-21", headers=headers
        )
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_water_intake_by_date("2012-12-21").first()
