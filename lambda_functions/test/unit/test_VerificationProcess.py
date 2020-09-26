import crud.operations as operations
from crud.model import User, Item, Level
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
import test.unit.event_creator as event_creator
import test.unit.setup_scenarios as scenarios


def test_verification_process_best_case(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)
    session = scenarios.create_levels_junior_and_senior_detectives(session)

    junior_detective1 = operations.get_user_by_id("1", True, session)
    junior_detective2 = operations.get_user_by_id("2", True, session)
    junior_detective3 = operations.get_user_by_id("3", True, session)
    junior_detective4 = operations.get_user_by_id("4", True, session)

    senior_detective1 = operations.get_user_by_id("11", True, session)
    senior_detective2 = operations.get_user_by_id("12", True, session)
    senior_detective3 = operations.get_user_by_id("13", True, session)
    senior_detective4 = operations.get_user_by_id("14", True, session)

    users = operations.get_all_users_db(True, session)
    assert len(users) == 8

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item = operations.create_item_db(item, True, session)

    items = operations.get_all_items_db(True, session)
    assert len(items) == 1

    # Junior detectives accepting item
    operations.accept_item_db(junior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 1

    operations.accept_item_db(junior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 2

    operations.accept_item_db(junior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(junior_detective4, item, True, session)

    # Senior detectives accepting item
    operations.accept_item_db(senior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 1

    operations.accept_item_db(senior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 2

    operations.accept_item_db(senior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(senior_detective4, item, True, session)

    # Junior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, junior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, junior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 2
    assert item.in_progress_reviews_level_1 == 2

    review_event = event_creator.get_review_event(
        item.id, junior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 1
    assert item.in_progress_reviews_level_1 == 1

    review_event = event_creator.get_review_event(
        item.id, junior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 0
    assert item.in_progress_reviews_level_1 == 0

    # Senior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, senior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, senior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 2
    assert item.in_progress_reviews_level_2 == 2

    review_event = event_creator.get_review_event(
        item.id, senior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 1
    assert item.in_progress_reviews_level_2 == 1

    review_event = event_creator.get_review_event(
        item.id, senior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 0
    assert item.in_progress_reviews_level_2 == 0

    assert item.status == "closed"
    assert item.result_score == 1


def test_verification_process_worst_case(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)

    session = scenarios.create_levels_junior_and_senior_detectives(session)

    junior_detective1 = operations.get_user_by_id("1", True, session)
    junior_detective2 = operations.get_user_by_id("2", True, session)
    junior_detective3 = operations.get_user_by_id("3", True, session)
    junior_detective4 = operations.get_user_by_id("4", True, session)

    senior_detective1 = operations.get_user_by_id("11", True, session)
    senior_detective2 = operations.get_user_by_id("12", True, session)
    senior_detective3 = operations.get_user_by_id("13", True, session)
    senior_detective4 = operations.get_user_by_id("14", True, session)

    users = operations.get_all_users_db(True, session)
    assert len(users) == 8

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item = operations.create_item_db(item, True, session)

    items = operations.get_all_items_db(True, session)
    assert len(items) == 1

    # Junior detectives accepting item
    operations.accept_item_db(junior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 1

    operations.accept_item_db(junior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 2

    operations.accept_item_db(junior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(junior_detective4, item, True, session)

    # Senior detectives accepting item
    operations.accept_item_db(senior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 1

    operations.accept_item_db(senior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 2

    operations.accept_item_db(senior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(senior_detective4, item, True, session)

    # Junior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, junior_detective4.id, 4)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, junior_detective1.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 2
    assert item.in_progress_reviews_level_1 == 2

    review_event = event_creator.get_review_event(
        item.id, junior_detective2.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 1
    assert item.in_progress_reviews_level_1 == 1

    review_event = event_creator.get_review_event(
        item.id, junior_detective3.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 0
    assert item.in_progress_reviews_level_1 == 0

    # Senior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, senior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, senior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 2
    assert item.in_progress_reviews_level_2 == 2

    review_event = event_creator.get_review_event(
        item.id, senior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 1
    assert item.in_progress_reviews_level_2 == 1

    review_event = event_creator.get_review_event(
        item.id, senior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)

    assert item.in_progress_reviews_level_2 == 0
    assert item.open_reviews_level_2 == 3
    assert item.open_reviews == 3
    assert item.result_score == None
