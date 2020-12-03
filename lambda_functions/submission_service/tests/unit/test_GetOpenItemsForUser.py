import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from ....tests.helper import event_creator, setup_scenarios, helper_functions

from core_layer.connection_handler import get_db_session
from core_layer.model.user_model import User
from core_layer.model.item_model import Item
from core_layer.model.level_model import Level

from core_layer.handler import user_handler, item_handler, review_handler


class TestGetOpenItems:
    def test_get_open_items_for_user(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")

        session = get_db_session(True, None)

        session = setup_scenarios.create_levels_junior_and_senior_detectives(
            session)
        session = setup_scenarios.create_questions(session)

        junior_detective1 = user_handler.get_user_by_id("1", True, session)
        junior_detective2 = user_handler.get_user_by_id("2", True, session)
        junior_detective3 = user_handler.get_user_by_id("3", True, session)
        junior_detective4 = user_handler.get_user_by_id("4", True, session)
        junior_detective5 = user_handler.get_user_by_id("5", True, session)

        senior_detective1 = user_handler.get_user_by_id("11", True, session)

        # Creating 5 items

        item1 = Item()
        item1.content = "Item 1"
        item1 = item_handler.create_item(item1, True, session)

        item2 = Item()
        item2.content = "Item 2"
        item2 = item_handler.create_item(item2, True, session)

        item3 = Item()
        item3.content = "Item 3"
        item3 = item_handler.create_item(item3, True, session)

        item4 = Item()
        item4.content = "Item 4"
        item4 = item_handler.create_item(item4, True, session)

        item5 = Item()
        item5.content = "Item 5"
        item5 = item_handler.create_item(item5, True, session)

        items = item_handler.get_all_items(True, session)
        assert len(items) == 5

        open_items_for_senior = item_handler.get_open_items_for_user(
            senior_detective1, 5, True, session)
        assert len(open_items_for_senior) == 5

        open_items_for_junior = item_handler.get_open_items_for_user(
            junior_detective1, 5, True, session)
        assert len(open_items_for_junior) == 5

        # JuniorDetective 1 accepting item 1
        jr1 = review_handler.create_review(
            junior_detective1, item1, True, session)
        open_item_after_accept = item_handler.get_open_items_for_user(
            junior_detective1, 5, True, session)
        assert len(open_item_after_accept) == 1

        item1 = item_handler.get_item_by_id(item1.id, True, session)
        assert item1.in_progress_reviews_level_1 == 1

        # Accepting event again should not create a new review
        review_handler.create_review(
            junior_detective1, item1, True, session)
        # app.create_review(accept_event, None, True, session)
        item1 = item_handler.get_item_by_id(item1.id, True, session)
        assert item1.in_progress_reviews_level_1 == 1

        # JuniorDetective 1 finishing review
        helper_functions.create_answers_for_review(jr1, 1, session)
        # review_event = event_creator.get_review_event(
        #    item1.id, junior_detective1.id, 1)
        # app.submit_review(review_event, None, True, session)

        # For JuniorDetective1 only 4 cases should be available
        open_items_after_submission = item_handler.get_open_items_for_user(
            junior_detective1, 5, True, session)
        assert len(open_items_after_submission) == 4

        open_items_limit_3 = item_handler.get_open_items_for_user(
            junior_detective1, 3, True, session)
        assert len(open_items_limit_3) == 3

        open_items_after_other_review = item_handler.get_open_items_for_user(
            junior_detective4, 5, True, session)
        assert len(open_items_after_other_review) == 5

        # 4 Junior Detectives reviewing Item 2
        jr1 = review_handler.create_review(
            junior_detective1, item2, True, session)
        jr2 = review_handler.create_review(
            junior_detective2, item2, True, session)
        jr3 = review_handler.create_review(
            junior_detective3, item2, True, session)
        jr4 = review_handler.create_review(
            junior_detective4, item2, True, session)

        helper_functions.create_answers_for_review(jr1, 1, session)
        helper_functions.create_answers_for_review(jr2, 1, session)
        helper_functions.create_answers_for_review(jr3, 1, session)
        helper_functions.create_answers_for_review(jr4, 1, session)

        # 4 Cases should be available for Detective 5

        open_items_after_other_review = item_handler.get_open_items_for_user(
            junior_detective5, 5, True, session)
        assert len(open_items_after_other_review) == 4

        # 5 cases should be available for senior
        open_items_for_senior = item_handler.get_open_items_for_user(
            senior_detective1, 5, True, session)
        assert len(open_items_for_senior) == 5

        # Senior detective accepting item 1
        sr1 = review_handler.create_review(
            senior_detective1, item1, True, session)

        open_item_after_accept = item_handler.get_open_items_for_user(
            senior_detective1, 5, True, session)
        assert len(open_item_after_accept) == 1

        # Senior detective finishing review
        helper_functions.create_answers_for_review(sr1, 1, session)

        # For SeniorDetective1 only 4 cases should be available
        open_items_after_submission = item_handler.get_open_items_for_user(
            senior_detective1, 5, True, session)
        assert len(open_items_after_submission) == 4

        # SeniorDetective 1 accepting item 3
        sr1 = review_handler.create_review(
            senior_detective1, item3, True, session)
        open_item_after_accept = item_handler.get_open_items_for_user(
            senior_detective1, 5, True, session)
        assert len(open_item_after_accept) == 1

        item3 = item_handler.get_item_by_id(item3.id, True, session)
        assert item3.in_progress_reviews_level_2 == 1

        # Accepting event again should not create a new review
        review_handler.create_review(
            senior_detective1, item3, True, session)
        item3 = item_handler.get_item_by_id(item3.id, True, session)
        assert item3.in_progress_reviews_level_2 == 1

        # SeniorDetective 1 finishing review
        helper_functions.create_answers_for_review(sr1, 1, session)

        open_items_for_senior = item_handler.get_open_items_for_user(
            senior_detective1, 5, True, session)
        assert len(open_items_for_senior) == 3
