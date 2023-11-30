from datetime import date

import pytest
from sqlalchemy import select

from src.repository.models import Food


@pytest.mark.parametrize("food_id, status_code", [(1, 200), (11, 404)])
def test_bare_get(client, food_id, status_code):
    result = client.simulate_get(f"/food/{food_id}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "food_date, status_code",
    [
        (str(date.today()), 200),
        ("1111-11-11", 404),
        ("11-11-1111", 400),
    ]
)
def test_get_from_date(client, food_date, status_code):
    result = client.simulate_get(f"/food/date/{food_date}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
              "date": "2011-12-21",
              "value": 10,
              "description": "eating in the park"
            },
            201
        ),
        (
            {
              "date": "2011-12-21",
              "value": 10,
            },
            400
        ),
        (
            {},
            400
        ),
        (
            {
              "date": "2011-12-21",
              "value": 10,
              "description": "eating in the park",
              "extra": "this should break"
            },
            500
        )
    ]
)
def test_post(client, body, status_code, session_factory):
    result = client.simulate_post(f"/food", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with session_factory() as session:
            query = select(Food).where(Food.date=="2011-12-21").fetch(1)
            assert session.scalar(query)

