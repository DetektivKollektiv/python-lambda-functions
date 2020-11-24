import crud.operations as operations
from crud.model import User, Level
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
import test.unit.event_creator as event_creator
import test.unit.setup_scenarios as scenarios


def test_level_system(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)

    session = scenarios.create_levels_junior_and_senior_detectives(session)

    junior_detective1 = operations.get_user_by_id("1", True, session)

    assert junior_detective1.level_id == 1
    assert junior_detective1.experience_points == 0

    operations.give_experience_point(junior_detective1.id, True, session)
    junior_detective1 = operations.get_user_by_id(
        junior_detective1.id, True, session)

    assert junior_detective1.level_id == 1
    assert junior_detective1.experience_points == 1

    for _ in range(5):
        operations.give_experience_point(
            junior_detective1.id, True, session)

    junior_detective1 = operations.get_user_by_id(
        junior_detective1.id, True, session)

    assert junior_detective1.level_id == 2
    assert junior_detective1.experience_points == 6
