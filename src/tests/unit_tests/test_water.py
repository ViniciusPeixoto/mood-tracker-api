from datetime import date

import pytest
from sqlalchemy import select

from src.repository.models import Water
from src.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("water_id, status_code", [(1, 200), (11, 404)])
def test_bare_get(client, water_id, status_code):
    result = client.simulate_get(f"/water-intake/{water_id}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "water_date, status_code",
    [
        (str(date.today()), 200),
        ("1111-11-11", 404),
        ("11-11-1111", 400),
    ],
)
def test_get_from_date(client, water_date, status_code):
    result = client.simulate_get(f"/water-intake/date/{water_date}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
                "date": "2009-12-21",
                "milliliters": 1000,
                "description": "drinking in the park",
                "pee": False,
            },
            201,
        ),
        (
            {
                "date": "2009-12-21",
                "milliliters": 1000,
            },
            400,
        ),
        ({}, 400),
        (
            {
                "date": "2009-12-21",
                "milliliters": 1000,
                "description": "drinking in the park",
                "pee": False,
                "extra": "this should break",
            },
            400,
        ),
    ],
)
def test_post(client, body, status_code, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/water-intake", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_water_intake_by_date("2009-12-21")


def test_bare_delete(client, uow: AbstractUnitOfWork):
    water_intake = Water(
        date="0005-01-01",
        milliliters="1",
        description="Water Intake for deletion",
        pee=True,
    )
    water_intake_id = None
    with uow:
        uow.repository.add_water_intake(water_intake)
        uow.commit()

        water_intake_id = uow.repository.get_water_intake_by_date("0005-01-01").id

    result = client.simulate_delete(f"/water-intake/{water_intake_id}")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_water_intake_by_id(water_intake_id)
