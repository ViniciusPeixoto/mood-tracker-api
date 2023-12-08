import json
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from falcon import testing
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.config.config import get_db_uri, settings
from api.main import run
from api.repository.models import Base, Exercises, Food, Humor, Mood, Water
from api.repository.unit_of_work import AbstractUnitOfWork, SQLAlchemyUnitOfWork


@pytest.fixture(scope="session", autouse=True)
def set_test_settings() -> None:
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    assert settings.current_env == "testing"


@pytest.fixture(scope="session")
def engine() -> Engine:
    engine = create_engine(get_db_uri())
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Session:
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    populate_db(engine, session)

    yield session

    session.close()


@pytest.fixture(scope="function")
def uow(db_session) -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork(session=db_session)


@pytest.fixture(scope="function")
def client(uow) -> testing.TestClient:
    return testing.TestClient(run(uow))


def populate_db(engine, db_session):
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

    for table in tables:
        db_session.add(table)
        db_session.flush()

    db_session.commit()
