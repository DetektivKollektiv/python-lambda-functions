import pytest

from core_layer.connection_handler import get_db_session
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.handler import user_handler
from ..helper import event_creator, setup_scenarios


def test_level_system(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")

    session = get_db_session(True, None)

    session = setup_scenarios.create_levels_junior_and_senior_detectives(
        session)

    junior_detective1 = user_handler.get_user_by_id("1", True, session)

    assert junior_detective1.level_id == 1
    assert junior_detective1.experience_points == 0

    user_handler.give_experience_point(junior_detective1.id, True, session)
    junior_detective1 = user_handler.get_user_by_id(
        junior_detective1.id, True, session)

    assert junior_detective1.level_id == 1
    assert junior_detective1.experience_points == 1

    for _ in range(5):
        user_handler.give_experience_point(
            junior_detective1.id, True, session)

    junior_detective1 = user_handler.get_user_by_id(
        junior_detective1.id, True, session)

    assert junior_detective1.level_id == 2
    assert junior_detective1.experience_points == 6
