import crud.operations as operations
from crud.model import User, Item
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
import test.unit.event_creator as event_creator


def test_get_open_items_for_user(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)

    # Creating junior detective
    junior_detective1 = User()
    junior_detective1.id = "1"
    junior_detective1.name = "Junior1"
    operations.create_user_db(junior_detective1, True, session)

    junior_detective2 = User()
    junior_detective2.id = "2"
    junior_detective2.name = "Junior2"
    operations.create_user_db(junior_detective2, True, session)

    junior_detective3 = User()
    junior_detective3.id = "3"
    junior_detective3.name = "Junior3"
    operations.create_user_db(junior_detective3, True, session)

    junior_detective4 = User()
    junior_detective4.id = "4"
    junior_detective4.name = "Junior4"
    operations.create_user_db(junior_detective4, True, session)

    # Create senior detectives
    senior_detective1 = User()
    senior_detective1.id = "11"
    senior_detective1.name = "Senior1"
    senior_detective1 = operations.create_user_db(
        senior_detective1, True, session)
    senior_detective1.level = 2

    senior_detective2 = User()
    senior_detective2.id = "12"
    senior_detective2.name = "Senior2"
    senior_detective2 = operations.create_user_db(
        senior_detective2, True, session)
    senior_detective2.level = 2

    session.merge(senior_detective1)
    session.merge(senior_detective2)
    session.commit()

    users = operations.get_all_users_db(True, session)
    assert len(users) == 6

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
    accept_event = event_creator.get_accept_event(
        junior_detective1.id, item1.id)
    app.accept_item(accept_event, None, True, session)
    open_item_after_accept = operations.get_open_items_for_user_db(
        junior_detective1, 5, True, session)
    assert len(open_item_after_accept) == 1

    item1 = operations.get_item_by_id(item1.id, True, session)
    assert item1.in_progress_reviews_level_1 == 1

    # Accepting event again
    app.accept_item(accept_event, None, True, session)
    item1 = operations.get_item_by_id(item1.id, True, session)
    assert item1.in_progress_reviews_level_1 == 1

    # JuniorDetective 1 finishing review
    review_event = event_creator.get_review_event(
        item1.id, junior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)

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

    # 3 Junior Detectives reviewing Item 2
    accept_event = event_creator.get_accept_event(
        junior_detective1.id, item2.id)
    app.accept_item(accept_event, None, True, session)

    accept_event = event_creator.get_accept_event(
        junior_detective2.id, item2.id)
    app.accept_item(accept_event, None, True, session)

    accept_event = event_creator.get_accept_event(
        junior_detective3.id, item2.id)
    app.accept_item(accept_event, None, True, session)

    review_event = event_creator.get_review_event(
        item2.id, junior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)

    review_event = event_creator.get_review_event(
        item2.id, junior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)

    review_event = event_creator.get_review_event(
        item2.id, junior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)

    # 4 Cases should be available for Detective 4

    open_items_after_other_review = operations.get_open_items_for_user_db(
        junior_detective4, 5, True, session)
    assert len(open_items_after_other_review) == 4

    open_items_for_senior = operations.get_open_items_for_user_db(
        senior_detective1, 5, True, session)
    assert len(open_items_for_senior) == 5

    accept_event = event_creator.get_accept_event(
        senior_detective1.id, item1.id)
    app.accept_item(accept_event, None, True, session)
    open_item_after_accept = operations.get_open_items_for_user_db(
        senior_detective1, 5, True, session)
    assert len(open_item_after_accept) == 1

    review_event = event_creator.get_review_event(
        item1.id, senior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)

    # For JuniorDetective1 only 4 cases should be available
    open_items_after_submission = operations.get_open_items_for_user_db(
        senior_detective1, 5, True, session)
    assert len(open_items_after_submission) == 4
