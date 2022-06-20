from archive_service.tests.unit.test_post_comment_on_item import item_id
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.review_model import Review
from core_layer.model.mail_model import Mail
from core_layer.handler import user_handler, mail_handler
from core_layer.db_handler import Session
from ....tests.helper import event_creator, setup_scenarios
from ...get_user import get_user
import json
from datetime import datetime

from core_layer.test.helper.fixtures import database_fixture

def test_get_user(database_fixture):

    with Session() as session:

        session = setup_scenarios.create_levels_junior_and_senior_detectives(
            session)
        junior_detective1 = user_handler.get_user_by_id("1", session)
        mail = mail_handler.create_mail(Mail(), session)
        junior_detective1.mail_id = mail.id

        event = event_creator.get_create_review_event(
            junior_detective1.id, "abc")
        resp = get_user(event, None)
        body = json.loads(resp["body"])

        assert body["mail_status"] == 'unconfirmed'
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
            body["sign_up_timestamp"], '%Y-%m-%dT%H:%M:%S').date()
        assert sign_up_date != datetime.today()

        item1 = Item(id='item1', status='closed')
        review1 = Review(
            id='review1', user_id=junior_detective1.id, item_id=item1.id)
        item2 = Item(id='item2', status='open')
        review2 = Review(
            id='review2', user_id=junior_detective1.id, item_id=item2.id)
        session.add_all([item1, item2, review1, review2])
        session.commit()
        resp = get_user(event, None)
        body = json.loads(resp["body"])
        assert len(body['closed_items']) == 1
        assert body['closed_items'][0]['id'] == 'item1'