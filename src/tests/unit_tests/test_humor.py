from datetime import date

import pytest
from sqlalchemy import select

from src.repository.models import Humor


@pytest.mark.parametrize("humor_id, status_code", [(1, 200), (11, 404)])
def test_bare_get(client, humor_id, status_code):
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
                "date": "2010-12-21",
                "value": 10,
                "description": "smiling in the park",
                "health_based": False,
            },
            201,
        ),
        (
            {
                "date": "2010-12-21",
                "value": 10,
            },
            400,
        ),
        ({}, 400),
        (
            {
                "date": "2010-12-21",
                "value": 10,
                "description": "smiling in the park",
                "health_based": False,
                "extra": "this should break",
            },
            500,
        ),
    ],
)
def test_post(client, body, status_code, session_factory):
    result = client.simulate_post(f"/humor", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with session_factory() as session:
            query = select(Humor).where(Humor.date == "2010-12-21").fetch(1)
            assert session.scalar(query)
