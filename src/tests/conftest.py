import json
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from falcon import testing
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import run
from config import get_db_uri, settings
from src.repository.models import Base, Exercises, Food, Humor, Mood, Water
from src.repository.unit_of_work import (AbstractUnitOfWork,
                                         SQLAlchemyUnitOfWork)


@pytest.fixture(scope="session", autouse=True)
def set_test_settings() -> None:
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    assert settings.current_env == "testing"


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(get_db_uri())


@pytest.fixture(scope="session")
def populate_db(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    params = {
        "exercises": Exercises(
            minutes=31, description="exercises description for testing"
        ),
        "food_habits": Food(value=10, description="food description for testing"),
        "humor": Humor(
            value=10,
            description="humor description for testing",
            health_based=True,
        ),
        "water_intake": Water(
            milliliters=1500,
            description="water intake description for testing",
            pee=True,
        ),
    }
    yesterday = str(date.today() - timedelta(days=1))
    no_mood_params = {
        "exercises": Exercises(
            date=yesterday, minutes=31, description="exercises description for testing"
        ),
        "food_habits": Food(
            date=yesterday, value=10, description="food description for testing"
        ),
        "humor": Humor(
            date=yesterday,
            value=10,
            description="humor description for testing",
            health_based=True,
        ),
        "water_intake": Water(
            date=yesterday,
            milliliters=1500,
            description="water intake description for testing",
            pee=True,
        ),
    }
    tables = [*params.values(), Mood(**params), *no_mood_params.values()]

    session = Session(engine)
    for table in tables:
        session.add(table)
        session.flush()

    session.commit()


@pytest.fixture(scope="session")
def session_factory(engine, populate_db) -> sessionmaker:
    yield sessionmaker(bind=engine)


@pytest.fixture(scope="session")
def uow(session_factory) -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork(session_factory=session_factory)


@pytest.fixture(scope="session")
def client(uow) -> testing.TestClient:
    return testing.TestClient(run(uow))
