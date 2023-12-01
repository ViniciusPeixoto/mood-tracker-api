from datetime import date, timedelta

import pytest
from sqlalchemy import select

from src.repository.models import Exercises, Food, Humor, Mood, Water
from src.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("mood_id, status_code", [(1, 200), (11, 404)])
def test_bare_get(client, mood_id, status_code):
    result = client.simulate_get(f"/mood/{mood_id}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "mood_date, status_code",
    [
        (str(date.today()), 200),
        ("1111-11-11", 404),
        ("11-11-1111", 400),
    ],
)
def test_get_from_date(client, mood_date, status_code):
    result = client.simulate_get(f"/mood/date/{mood_date}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
                "date": "2012-12-21",
                "humor": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Humor de teste.",
                    "health_based": False,
                },
                "water_intake": {
                    "date": "2012-12-21",
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False,
                },
                "exercises": {
                    "date": "2012-12-21",
                    "minutes": 10,
                    "description": "Exercícios de teste.",
                },
                "food_habits": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Alimentação de teste.",
                },
            },
            201,
        ),
        (
            {
                "date": "2012-12-21",
                "humor": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Humor de teste.",
                    "health_based": False,
                },
                "water_intake": {
                    "date": "2012-12-21",
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False,
                },
                "food_habits": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Alimentação de teste.",
                },
            },
            400,
        ),
        ({}, 400),
        (
            {
                "date": "2012-12-21",
                "humor": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Humor de teste.",
                    "health_based": False,
                },
                "water_intake": {
                    "date": "2012-12-21",
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False,
                },
                "exercises": {
                    "date": "2012-12-21",
                    "minutes": 10,
                    "description": "Exercícios de teste.",
                },
                "food_habits": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Alimentação de teste.",
                },
                "extra": {"this": "should break things"},
            },
            400,
        ),
    ],
)
def test_bare_post(client, body, status_code, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/mood", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_mood_by_date("2012-12-21")


def test_bare_delete(client, uow: AbstractUnitOfWork):
    water_intake = Water(
        date="0001-01-01",
        milliliters="1",
        description="Water Intake for deletion",
        pee=True,
    )
    food = Food(date="0001-01-01", value="1", description="Food for deletion")
    exercise = Exercises(
        date="0001-01-01", minutes=10, description="Exercise for deletion"
    )
    humor = Humor(
        date="0001-01-01",
        value="1",
        description="Humor for deletion",
        health_based=True,
    )
    mood = Mood(
        date="0001-01-01",
        humor=humor,
        food_habits=food,
        exercises=exercise,
        water_intake=water_intake,
    )
    mood_id = None
    with uow:
        uow.repository.add_mood(mood)
        uow.commit()

        mood_id = uow.repository.get_mood_by_date("0001-01-01").id

    result = client.simulate_delete(f"/mood/{mood_id}")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_mood_by_id(mood_id)
