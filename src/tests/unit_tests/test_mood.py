from datetime import date, timedelta

import pytest
from sqlalchemy import select

from src.repository.models import Food


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
    ]
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
                    "health_based": False
                },
                "water_intake": {
                    "date": "2012-12-21",
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False
                },
                "exercises": {
                    "date": "2012-12-21",
                    "minutes": 10,
                    "description": "Exercícios de teste."
                },
                "food_habits": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Alimentação de teste."
                }
            },
            201
        ),
        (
            {
                "date": "2012-12-21",
                "humor": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Humor de teste.",
                    "health_based": False
                },
                "water_intake": {
                    "date": "2012-12-21",
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False
                },
                "food_habits": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Alimentação de teste."
                }
            },
            400
        ),
        (
            {},
            400
        ),
        (
            {
                "date": "2012-12-21",
                "humor": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Humor de teste.",
                    "health_based": False
                },
                "water_intake": {
                    "date": "2012-12-21",
                    "milliliters": 10,
                    "description": "Consumo de água de teste.",
                    "pee": False
                },
                "exercises": {
                    "date": "2012-12-21",
                    "minutes": 10,
                    "description": "Exercícios de teste."
                },
                "food_habits": {
                    "date": "2012-12-21",
                    "value": 10,
                    "description": "Alimentação de teste."
                },
                "extra": {"this": "should break things"}
            },
            400
        )
    ]
)
def test_bare_post(client, body, status_code, session_factory):
    result = client.simulate_post(f"/mood", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with session_factory() as session:
            query = select(Food).where(Food.date=="2012-12-21").fetch(1)
            assert session.scalar(query)


@pytest.mark.parametrize(
    "mood_date, status_code",
    [
        (str(date.today() - timedelta(days=1)), 201),
        ("1111-11-11", 404),
        ("11-11-1111", 400),
    ]
)
def test_get_from_date(client, mood_date, status_code):
    result = client.simulate_post(f"/mood/date/{mood_date}")

    assert result.status_code == status_code
