import crud.operations as operations
from crud.model import User, Level
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
import test.unit.event_creator as event_creator
import test.unit.setup_scenarios as scenarios
import json


def test_get_user(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)

    session = scenarios.create_levels_junior_and_senior_detectives(session)
    junior_detective1 = operations.get_user_by_id("1", True, session)

    event = event_creator.get_create_review_event(junior_detective1.id, "abc")
    resp = app.get_user(event, None, True, session)
    body = json.loads(resp["body"])

    assert body["id"] == junior_detective1.id
    assert body["level"] == 1
    assert body["level_description"] == "Junior"
