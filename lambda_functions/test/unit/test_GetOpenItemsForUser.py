import crud.operations as operations
from crud.model import User, Item, Level
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
import test.unit.event_creator as event_creator
import test.unit.setup_scenarios as scenarios
import test.unit.helper_functions as helper


class TestGetOpenItems:
    def test_get_open_items_for_user(self, monkeypatch):
        monkeypatch.setenv("DBNAME", "Test")
        import app

        session = operations.get_db_session(True, None)

        session = scenarios.create_levels_junior_and_senior_detectives(session)
        session = scenarios.create_questions(session)

        junior_detective1 = operations.get_user_by_id("1", True, session)
        junior_detective2 = operations.get_user_by_id("2", True, session)
        junior_detective3 = operations.get_user_by_id("3", True, session)
        junior_detective4 = operations.get_user_by_id("4", True, session)
        junior_detective5 = operations.get_user_by_id("5", True, session)

        senior_detective1 = operations.get_user_by_id("11", True, session)

        # Creating 5 items

        item1 = Item()
        item1.content = "Item 1"
        item1 = operations.create_item_db(item1, True, session)

        item2 = Item()
        item2.content = "Item 2"
        item2 = operations.create_item_db(item2, True, session)

        item3 = Item()
        item3.content = "Item 3"
        item3 = operations.create_item_db(item3, True, session)

        item4 = Item()
        item4.content = "Item 4"
        item4 = operations.create_item_db(item4, True, session)

        item5 = Item()
        item5.content = "Item 5"
        item5 = operations.create_item_db(item5, True, session)

        items = operations.get_all_items_db(True, session)
        assert len(items) == 5

        open_items_for_senior = operations.get_open_items_for_user_db(
            senior_detective1, 5, True, session)
        assert len(open_items_for_senior) == 5

        open_items_for_junior = operations.get_open_items_for_user_db(
            junior_detective1, 5, True, session)
        assert len(open_items_for_junior) == 5

        # JuniorDetective 1 accepting item 1
        jr1 = operations.accept_item_db(
            junior_detective1, item1, True, session)
        open_item_after_accept = operations.get_open_items_for_user_db(
            junior_detective1, 5, True, session)
        assert len(open_item_after_accept) == 1

        item1 = operations.get_item_by_id(item1.id, True, session)
        assert item1.in_progress_reviews_level_1 == 1

        # Accepting event again should not create a new review
        operations.accept_item_db(
            junior_detective1, item1, True, session)
        # app.create_review(accept_event, None, True, session)
        item1 = operations.get_item_by_id(item1.id, True, session)
        assert item1.in_progress_reviews_level_1 == 1

        # JuniorDetective 1 finishing review
        helper.create_answers_for_review(jr1, 1, session)
        # review_event = event_creator.get_review_event(
        #    item1.id, junior_detective1.id, 1)
        # app.submit_review(review_event, None, True, session)

        # For JuniorDetective1 only 4 cases should be available
        open_items_after_submission = operations.get_open_items_for_user_db(
            junior_detective1, 5, True, session)
        assert len(open_items_after_submission) == 4

        open_items_limit_3 = operations.get_open_items_for_user_db(
            junior_detective1, 3, True, session)
        assert len(open_items_limit_3) == 3

        open_items_after_other_review = operations.get_open_items_for_user_db(
            junior_detective4, 5, True, session)
        assert len(open_items_after_other_review) == 5

        # 4 Junior Detectives reviewing Item 2
        jr1 = operations.accept_item_db(
            junior_detective1, item2, True, session)
        jr2 = operations.accept_item_db(
            junior_detective2, item2, True, session)
        jr3 = operations.accept_item_db(
            junior_detective3, item2, True, session)
        jr4 = operations.accept_item_db(
            junior_detective4, item2, True, session)

        helper.create_answers_for_review(jr1, 1, session)
        helper.create_answers_for_review(jr2, 1, session)
        helper.create_answers_for_review(jr3, 1, session)
        helper.create_answers_for_review(jr4, 1, session)

        # 4 Cases should be available for Detective 5

        open_items_after_other_review = operations.get_open_items_for_user_db(
            junior_detective5, 5, True, session)
        assert len(open_items_after_other_review) == 4

        # 5 cases should be available for senior
        open_items_for_senior = operations.get_open_items_for_user_db(
            senior_detective1, 5, True, session)
        assert len(open_items_for_senior) == 5

        # Senior detective accepting item 1
        sr1 = operations.accept_item_db(
            senior_detective1, item1, True, session)

        open_item_after_accept = operations.get_open_items_for_user_db(
            senior_detective1, 5, True, session)
        assert len(open_item_after_accept) == 1

        # Senior detective finishing review
        helper.create_answers_for_review(sr1, 1, session)

        # For SeniorDetective1 only 4 cases should be available
        open_items_after_submission = operations.get_open_items_for_user_db(
            senior_detective1, 5, True, session)
        assert len(open_items_after_submission) == 4

        # SeniorDetective 1 accepting item 3
        sr1 = operations.accept_item_db(
            senior_detective1, item3, True, session)
        open_item_after_accept = operations.get_open_items_for_user_db(
            senior_detective1, 5, True, session)
        assert len(open_item_after_accept) == 1

        item3 = operations.get_item_by_id(item3.id, True, session)
        assert item3.in_progress_reviews_level_2 == 1

        # Accepting event again should not create a new review
        operations.accept_item_db(
            senior_detective1, item3, True, session)
        item3 = operations.get_item_by_id(item3.id, True, session)
        assert item3.in_progress_reviews_level_2 == 1

        # SeniorDetective 1 finishing review
        helper.create_answers_for_review(sr1, 1, session)

        open_items_for_senior = operations.get_open_items_for_user_db(
            senior_detective1, 5, True, session)
        assert len(open_items_for_senior) == 3
