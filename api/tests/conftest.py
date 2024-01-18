from datetime import date

import jwt
import pytest
from falcon import testing
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.config.config import get_db_uri, get_jwt_secret_key, settings
from api.main import run
from api.repository.models import (
    Base,
    Exercises,
    Food,
    Humor,
    Mood,
    Sleep,
    User,
    UserAuth,
    Water,
)
from api.repository.unit_of_work import AbstractUnitOfWork, SQLAlchemyUnitOfWork


@pytest.fixture(scope="session", autouse=True)
def set_test_settings() -> None:
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    assert settings.current_env == "testing"


@pytest.fixture(scope="function")
def create_access_token() -> str:
    secret_key = get_jwt_secret_key()
    data = {
        "user_auth_username": "test_username",
    }
    token = jwt.encode(data, secret_key, algorithm="HS256")
    return token


@pytest.fixture(scope="function")
def headers(create_access_token) -> dict:
    return {"Authorization": f"Bearer: {create_access_token}"}


@pytest.fixture(scope="session")
def engine() -> Engine:
    engine = create_engine(get_db_uri())
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine, create_access_token) -> Session:
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    populate_db(engine, session, create_access_token)

    yield session

    session.close()


@pytest.fixture(scope="function")
def uow(db_session) -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork(session=db_session)


@pytest.fixture(scope="function")
def client(uow) -> testing.TestClient:
    return testing.TestClient(run(uow))


def populate_db(engine, db_session, create_access_token):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    today = date.today()

    # test user and test mood
    db_session.add(User())
    db_session.add(
        UserAuth(
            username="test_username",
            password="test_password",
            created_at=today,
            last_login=today,
            token=create_access_token,
            user_id=1,
        )
    )
    db_session.add(Mood(user_id=1))
    db_session.commit()

    params = {
        "exercises": Exercises(
            minutes=31, description="exercises description for testing", mood_id=1
        ),
        "food_habits": Food(
            value=10, description="food description for testing", mood_id=1
        ),
        "humor": Humor(
            value=10,
            description="humor description for testing",
            health_based=True,
            mood_id=1,
        ),
        "water_intake": Water(
            milliliters=1500,
            description="water intake description for testing",
            pee=True,
            mood_id=1,
        ),
        "sleep": Sleep(
            value=10,
            minutes=480,
            description="sleep description for testing",
            mood_id=1,
        )
    }

    for table in params.values():
        db_session.add(table)
        db_session.flush()

    db_session.commit()
