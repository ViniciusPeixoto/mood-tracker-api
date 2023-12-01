from datetime import date

import pytest
from sqlalchemy import select

from src.repository.models import Exercises
from src.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("exercise_id, status_code", [(1, 200), (11, 404)])
def test_bare_get(client, exercise_id, status_code):
    result = client.simulate_get(f"/exercises/{exercise_id}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "exercise_date, status_code",
    [
        (str(date.today()), 200),
        ("1111-11-11", 404),
        ("11-11-1111", 400),
    ],
)
def test_get_from_date(client, exercise_date, status_code):
    result = client.simulate_get(f"/exercises/date/{exercise_date}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {"date": "2009-12-21", "minutes": 15, "description": "running in the park"},
            201,
        ),
        (
            {
                "date": "2009-12-21",
                "minutes": 15,
            },
            400,
        ),
        ({}, 400),
        (
            {
                "date": "2009-12-21",
                "minutes": 15,
                "description": "running in the park",
                "extra": "this should break",
            },
            400,
        ),
    ],
)
def test_post(client, body, status_code, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/exercises", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_exercises_by_date("2009-12-21")


def test_bare_delete(client, uow: AbstractUnitOfWork):
    exercise = Exercises(
        date="0002-01-01", minutes=10, description="Exercise for deletion"
    )
    exercise_id = None
    with uow:
        uow.repository.add_exercises(exercise)
        uow.commit()

        exercise_id = uow.repository.get_exercises_by_date("0002-01-01").id

    result = client.simulate_delete(f"/exercises/{exercise_id}")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_exercises_by_id(exercise_id)
