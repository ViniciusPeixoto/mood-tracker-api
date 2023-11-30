import pytest
from sqlalchemy.sql import text


def test_database(session_factory):
    session = session_factory()
    result = session.execute(text("SELECT * FROM user_mood"))

    # fetchall returns a list, so if database is working,
    # then this list should not be empty
    assert result.fetchall()
