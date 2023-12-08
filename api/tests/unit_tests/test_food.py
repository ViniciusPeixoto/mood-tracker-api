from datetime import date

import pytest
from sqlalchemy import select

from api.repository.models import Food
from api.repository.unit_of_work import AbstractUnitOfWork


@pytest.mark.parametrize("food_id, status_code", [(1, 200), (11, 404)])
def test_get(client, food_id, status_code):
    result = client.simulate_get(f"/food/{food_id}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "food_date, status_code",
    [
        (str(date.today()), 200),
        ("1111-11-11", 404),
        ("11-11-1111", 400),
    ],
)
def test_get_from_date(client, food_date, status_code):
    result = client.simulate_get(f"/food/date/{food_date}")

    assert result.status_code == status_code


@pytest.mark.parametrize(
    "body, status_code",
    [
        ({"date": "2012-12-21", "value": 10, "description": "eating in the park"}, 201),
        (
            {
                "date": "2012-12-21",
                "value": 10,
            },
            400,
        ),
        ({}, 400),
        (
            {
                "date": "2012-12-21",
                "value": 10,
                "description": "eating in the park",
                "extra": "this should break",
            },
            400,
        ),
    ],
)
def test_post(client, body, status_code, uow: AbstractUnitOfWork):
    result = client.simulate_post(f"/food", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        with uow:
            assert uow.repository.get_food_habits_by_date("2012-12-21").first()


@pytest.mark.parametrize(
    "body, status_code",
    [
        (
            {
                "value": 10,
                "description": "eating in the park",
            },
            200,
        ),
        (
            {
                "value": 10,
            },
            200,
        ),
        ({}, 400),
        (
            {
                "value": 10,
                "description": "eating in the park",
                "extra": "this should break",
            },
            400,
        ),
    ],
)
def test_update(client, body, status_code, uow: AbstractUnitOfWork):
    food_habits_params = {
        "date": "2012-12-21",
        "value": "1",
        "description": "Food for updating",
    }
    food_habits = Food(**food_habits_params)
    food_id = None

    with uow:
        uow.repository.add_food_habits(food_habits)
        uow.flush()

        food_id = uow.repository.get_food_habits_by_date("2012-12-21").first().id

        result = client.simulate_patch(f"/food/{food_id}", json=body)

    assert result.status_code == status_code

    if result.status_code < 400:
        food_habits_params.update(body)
        with uow:
            assert uow.repository.get_food_habits_by_date("2012-12-21").first() == Food(
                **food_habits_params
            )


def test_delete(client, uow: AbstractUnitOfWork):
    food = Food(date="2012-12-21", value="1", description="Food for deletion")
    food_id = None

    with uow:
        uow.repository.add_food_habits(food)
        uow.flush()

        food_id = uow.repository.get_food_habits_by_date("2012-12-21").first().id

        result = client.simulate_delete(f"/food/{food_id}")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_food_habits_by_id(food_id)


def test_delete_date(client, uow: AbstractUnitOfWork):
    foods = [
        Food(date="2012-12-21", value="1", description="First Food for deletion"),
        Food(date="2012-12-21", value="2", description="Second Food for deletion")
    ]

    with uow:
        for food in foods:
            uow.repository.add_food_habits(food)
        uow.flush()

        result = client.simulate_delete(f"/food/date/2012-12-21")
    assert result.status_code == 204

    with uow:
        assert not uow.repository.get_food_habits_by_date("2012-12-21").first()
