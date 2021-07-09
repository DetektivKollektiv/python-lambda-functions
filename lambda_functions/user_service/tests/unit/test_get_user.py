from core_layer.model.user_model import User
from core_layer.handler import user_handler
from core_layer.db_handler import Session
from ....tests.helper import event_creator, setup_scenarios
from ...get_user import get_user
import json
from datetime import datetime


def test_get_user():

    with Session() as session:

        session = setup_scenarios.create_levels_junior_and_senior_detectives(session)
        junior_detective1 = user_handler.get_user_by_id("1", session)

        event = event_creator.get_create_review_event(junior_detective1.id, "abc")
        resp = get_user(event, None)
        body = json.loads(resp["body"])

        assert body["id"] == junior_detective1.id
        assert body["level"] == 1
        assert body["level_description"] == "Junior"
        assert body["progress"] == 0
        assert body["total_rank"] == session.query(User).count()
        assert body["level_rank"] == session.query(User).filter(
            User.level_id == junior_detective1.level_id).count()
        assert body["solved_cases_total"] == 0
        assert body["solved_cases_today"] == 0
        assert body["exp_needed"] == 5
        sign_up_date = datetime.strptime(
            body["sign_up_timestamp"], '%Y-%m-%d %H:%M:%S').date()
        assert sign_up_date != datetime.today()
