from datetime import date, timedelta

import pytest
from sqlalchemy import select

from src.repository.models import Exercises, Food, Humor, Mood, Water
from src.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("mood_id, status_code", [(1, 200), (11, 404)])
def test_get(client, mood_id, status_code):
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
def test_post(client, body, status_code, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/mood", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_mood_by_date("2012-12-21")


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
                "humor": {
                    "value": 10,
                    "description": "Humor de teste.",
                    "health_based": False,
                },
                "water_intake": {
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False,
                },
                "exercises": {
                    "minutes": 10,
                    "description": "Exercícios de teste.",
                },
                "food_habits": {
                    "value": 10,
                    "description": "Alimentação de teste.",
                },
            },
            200,
        ),
        (
            {
                "food_habits": {
                    "value": 10,
                    "description": "Alimentação de teste.",
                }
            },
            200,
        ),
        ({}, 400),
        (
            {
                "humor": {
                    "value": 10,
                    "description": "Humor de teste.",
                    "health_based": False,
                },
                "water_intake": {
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False,
                },
                "exercises": {
                    "minutes": 10,
                    "description": "Exercícios de teste.",
                },
                "food_habits": {
                    "value": 10,
                    "description": "Alimentação de teste.",
                },
                "extra": {"this": "should break things"},
            },
            400,
        ),
    ],
)
def test_update(client, body, status_code, uow: AbstractUnitOfWork):
    mood_params = {
        "date":"2012-12-21",
        "humor": Humor(**{
            "date":"2012-12-21",
            "value": 1,
            "description": "Humor for updating.",
            "health_based": True,
        }),
        "water_intake": Water(**{
            "date":"2012-12-21",
            "milliliters": 1,
            "description": "Consumo de água for updating.",
            "pee": True,
        }),
        "exercises": Exercises(**{
            "date":"2012-12-21",
            "minutes": 1,
            "description": "Exercícios for updating.",
        }),
        "food_habits": Food(**{
            "date":"2012-12-21",
            "value": 1,
            "description": "Alimentação for updating.",
        })
    }
    mood = Mood(**mood_params)
    mood_id = None
    with uow:
        uow.repository.add_mood(mood)
        uow.flush()

        mood_id = uow.repository.get_mood_by_date("2012-12-21").id

        result = client.simulate_patch(f"/mood/{mood_id}", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        mood_params = {
            "date":"2012-12-21",
            "humor": Humor(**{
                "date":"2012-12-21",
                "value": 1,
                "description": "Humor for updating.",
                "health_based": True,
            }),
            "water_intake": Water(**{
                "date":"2012-12-21",
                "milliliters": 1,
                "description": "Consumo de água for updating.",
                "pee": True,
            }),
            "exercises": Exercises(**{
                "date":"2012-12-21",
                "minutes": 1,
                "description": "Exercícios for updating.",
            }),
            "food_habits": Food(**{
                "date":"2012-12-21",
                "value": 1,
                "description": "Alimentação for updating.",
            })
        }
        params_classes = {
            "humor": Humor,
            "water_intake": Water,
            "exercises": Exercises,
            "food_habits": Food,
        }
        mood_updated_params = {
                key: params_classes.get(key)(date="2012-12-21",**body.get(key))
                for key in body
            }
        mood_params.update(mood_updated_params)
        with uow:
            expected = Mood(**mood_params)
            updated = uow.repository.get_mood_by_date("2012-12-21")
            assert updated == expected


def test_delete(client, uow: AbstractUnitOfWork):
    water_intake = Water(
        date="2012-12-21",
        milliliters="1",
        description="Water Intake for deletion",
        pee=True,
    )
    food = Food(date="2012-12-21", value="1", description="Food for deletion")
    exercise = Exercises(
        date="2012-12-21", minutes=10, description="Exercise for deletion"
    )
    humor = Humor(
        date="2012-12-21",
        value="1",
        description="Humor for deletion",
        health_based=True,
    )
    mood = Mood(
        date="2012-12-21",
        humor=humor,
        food_habits=food,
        exercises=exercise,
        water_intake=water_intake,
    )
    mood_id = None
    with uow:
        uow.repository.add_mood(mood)
        uow.flush()

        mood_id = uow.repository.get_mood_by_date("2012-12-21").id

        result = client.simulate_delete(f"/mood/{mood_id}")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_mood_by_id(mood_id)
