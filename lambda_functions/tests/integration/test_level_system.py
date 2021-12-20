from core_layer.db_handler import Session
from core_layer.handler import user_handler
from ..helper import setup_scenarios


def test_level_system():

    with Session() as session:

        session = setup_scenarios.create_levels_junior_and_senior_detectives(session)

        junior_detective1 = user_handler.get_user_by_id("1", session)

        assert junior_detective1.level_id == 1
        assert junior_detective1.experience_points == 0

        user_handler.give_experience_point(junior_detective1.id, session)
        junior_detective1 = user_handler.get_user_by_id(junior_detective1.id, session)

        assert junior_detective1.level_id == 1
        assert junior_detective1.experience_points == 1

        for _ in range(5):
            user_handler.give_experience_point(junior_detective1.id, session)

        junior_detective1 = user_handler.get_user_by_id(junior_detective1.id, session)

        assert junior_detective1.level_id == 2
        assert junior_detective1.experience_points == 6
