import pytest
from sqlalchemy.sql import text


def test_database(db_session):
    result = db_session.execute(text("SELECT * FROM user_mood"))

    # fetchall returns a list, so if database is working,
    # then this list should not be empty
    assert result.fetchall()
