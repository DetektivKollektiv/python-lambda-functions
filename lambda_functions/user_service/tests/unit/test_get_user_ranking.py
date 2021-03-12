from core_layer.model.user_model import User
from core_layer.connection_handler import get_db_session
import pytest
from core_layer.handler import user_handler
from ....tests.helper import event_creator, setup_scenarios
from ...get_user_ranking import get_user_ranking
import json


def test_get_user_ranking(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")

    session = get_db_session(True, None)
    session = setup_scenarios.create_users_for_ranking(session)
    
    my_detective = user_handler.get_user_by_id("999", True, session)

    event = event_creator.get_create_review_event(my_detective.id, None)

    resp = get_user_ranking(event, None, True, session)
    user_rankings = json.loads(resp["body"])
    
    assert len(user_rankings) == 3
    assert ("top_users" in user_rankings) == True
    assert ("top_users_by_level" in user_rankings) == True
    assert ("top_users_by_period" in user_rankings) == True

    top_users = user_rankings['top_users']
    
    # ten top users in list
    assert len(top_users) == 10
    assert top_users[0]['experience_points'] == 60
    # each EXP should be higher than the next (for the sorted column "experience_points")
    assert int(top_users[0]['experience_points']) > int(top_users[1]['experience_points'])

    top_users_by_level = user_rankings['top_users_by_level']

    assert len(top_users_by_level) == 10
    assert int(top_users_by_level[0]['experience_points']) > int(top_users_by_level[1]['experience_points'])
    # the first/ top user's experience points
    assert top_users_by_level[0]['experience_points'] == 40
    # My User's experience points:
    assert top_users_by_level[5]['experience_points'] == 35
    # the last user's experience points
    assert top_users_by_level[9]['experience_points'] == 32
    # the first/ top users's level (= my level)
    assert top_users_by_level[0]['level'] == 2
    # the last users's level (= my level)
    assert top_users_by_level[9]['level'] == 2

    top_users_by_period = user_rankings['top_users_by_period']
     
    # For period = 1 week only 7 users found
    assert len(top_users_by_period) == 7
    assert int(top_users_by_period[0]['experience_points']) > int(top_users_by_period[1]['experience_points'])
    assert top_users_by_period[1]['experience_points'] == 6
    assert top_users_by_period[6]['experience_points'] == 1     
    