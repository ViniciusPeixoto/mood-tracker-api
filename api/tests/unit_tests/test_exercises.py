from datetime import date

import pytest

from api.repository.models import Exercises
from api.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("exercise_id, status_code", [(1, 200), (11, 404)])
def test_get(client, exercise_id, status_code):
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
            {"date": "2012-12-21", "minutes": 15, "description": "running in the park"},
            201,
        ),
        (
            {
                "date": "2012-12-21",
                "minutes": 15,
            },
            400,
        ),
        ({}, 400),
        (
            {
                "date": "2012-12-21",
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
            assert uow.repository.get_exercises_by_date("2012-12-21").first()


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
                "minutes": 10,
                "description": "running in the park",
            },
            200,
        ),
        (
            {
                "minutes": 10,
            },
            200,
        ),
        ({}, 400),
        (
            {
                "minutes": 10,
                "description": "running in the park",
                "extra": "this should break",
            },
            400,
        ),
    ],
)
def test_update(client, body, status_code, uow: AbstractUnitOfWork):
    exercises_params = {
        "date": "2012-12-21",
        "minutes": "1",
        "description": "Exercises for updating",
    }
    exercises = Exercises(**exercises_params)
    exercises_id = None
    with uow:
        uow.repository.add_exercises(exercises)
        uow.flush()

        exercises_id = uow.repository.get_exercises_by_date("2012-12-21").first().id

        result = client.simulate_patch(f"/exercises/{exercises_id}", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        exercises_params.update(body)
        with uow:
            assert uow.repository.get_exercises_by_date("2012-12-21").first() == Exercises(
                **exercises_params
            )


def test_delete(client, uow: AbstractUnitOfWork):
    exercise = Exercises(
        date="2012-12-21", minutes=10, description="Exercise for deletion"
    )
    exercise_id = None
    with uow:
        uow.repository.add_exercises(exercise)
        uow.flush()

        exercise_id = uow.repository.get_exercises_by_date("2012-12-21").first().id

        result = client.simulate_delete(f"/exercises/{exercise_id}")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_exercises_by_id(exercise_id)


def test_delete_date(client, uow: AbstractUnitOfWork):
    exercises = [
        Exercises(
        date="2012-12-21", minutes=10, description="First Exercise for deletion"
        ),
        Exercises(
        date="2012-12-21", minutes=15, description="Second Exercise for deletion"
        ),
    ]
    with uow:
        for exercise in exercises:
            uow.repository.add_exercises(exercise)
        uow.flush()

        result = client.simulate_delete(f"/exercises/date/2012-12-21")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_exercises_by_date("2012-12-21").first()
