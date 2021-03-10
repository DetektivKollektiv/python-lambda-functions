from core_layer.model.user_model import User
from core_layer.connection_handler import get_db_session
import pytest
from ....tests.helper import event_creator, setup_scenarios
from ...get_top_users import get_top_users
import json


def test_get_top_users(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")

    session = get_db_session(True, None)
    session = setup_scenarios.create_users_for_ranking(session)

    event = None
    resp = get_top_users(event, None, True, session)
    users = json.loads(resp["body"])

    assert users[0]['experience_points'] == 60

    # each should be higher than the next (for the sorted column "experience_points")
    assert int(users[0]['experience_points']) > int(users[1]['experience_points'])

    # 10 is hardcoded at the moment as the num users to fetch for this
    assert len(users) == 10
