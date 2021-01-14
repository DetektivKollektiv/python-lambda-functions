from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.handler import user_handler
from core_layer.connection_handler import get_db_session
import pytest
from ....tests.helper import event_creator, setup_scenarios
from ...get_user import get_user
import json


def test_get_user(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")

    session = get_db_session(True, None)

    session = setup_scenarios.create_levels_junior_and_senior_detectives(
        session)
    junior_detective1 = user_handler.get_user_by_id("1", True, session)

    event = event_creator.get_create_review_event(junior_detective1.id, "abc")
    resp = get_user(event, None, True, session)
    body = json.loads(resp["body"])

    assert body["id"] == junior_detective1.id
    assert body["level"] == 1
    assert body["level_description"] == "Junior"
    assert body["progress"] == 0
    assert body["total_rank"] == session.query(User).count()
    assert body["level_rank"] == session.query(User).filter(
        User.level_id == junior_detective1.level_id).count()
