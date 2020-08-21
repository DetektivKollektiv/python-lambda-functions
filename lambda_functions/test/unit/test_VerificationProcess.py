import crud.operations as operations
from crud.model import User, Item
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker


def test_verification_process_best_case(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)

    # Creating junior detectives
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

    senior_detective3 = User()
    senior_detective3.id = "13"
    senior_detective3.name = "Senior3"
    senior_detective3 = operations.create_user_db(
        senior_detective3, True, session)
    senior_detective3.level = 2

    senior_detective4 = User()
    senior_detective4.id = "14"
    senior_detective4.name = "Senior4"
    senior_detective4 = operations.create_user_db(
        senior_detective4, True, session)
    senior_detective4.level = 2

    session.merge(senior_detective1)
    session.merge(senior_detective2)
    session.merge(senior_detective3)
    session.merge(senior_detective4)
    session.commit()

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

    review_event = get_review_event(item.id, junior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = get_review_event(item.id, junior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 2
    assert item.in_progress_reviews_level_1 == 2

    review_event = get_review_event(item.id, junior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 1
    assert item.in_progress_reviews_level_1 == 1

    review_event = get_review_event(item.id, junior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 0
    assert item.in_progress_reviews_level_1 == 0

    # Senior detectives reviewing item

    review_event = get_review_event(item.id, senior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = get_review_event(item.id, senior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 2
    assert item.in_progress_reviews_level_2 == 2

    review_event = get_review_event(item.id, senior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 1
    assert item.in_progress_reviews_level_2 == 1

    review_event = get_review_event(item.id, senior_detective3.id, 1)
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

    # Creating junior detectives
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

    senior_detective3 = User()
    senior_detective3.id = "13"
    senior_detective3.name = "Senior3"
    senior_detective3 = operations.create_user_db(
        senior_detective3, True, session)
    senior_detective3.level = 2

    senior_detective4 = User()
    senior_detective4.id = "14"
    senior_detective4.name = "Senior4"
    senior_detective4 = operations.create_user_db(
        senior_detective4, True, session)
    senior_detective4.level = 2

    session.merge(senior_detective1)
    session.merge(senior_detective2)
    session.merge(senior_detective3)
    session.merge(senior_detective4)
    session.commit()

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

    review_event = get_review_event(item.id, junior_detective4.id, 4)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = get_review_event(item.id, junior_detective1.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 2
    assert item.in_progress_reviews_level_1 == 2

    review_event = get_review_event(item.id, junior_detective2.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 1
    assert item.in_progress_reviews_level_1 == 1

    review_event = get_review_event(item.id, junior_detective3.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 0
    assert item.in_progress_reviews_level_1 == 0

    # Senior detectives reviewing item

    review_event = get_review_event(item.id, senior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = get_review_event(item.id, senior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 2
    assert item.in_progress_reviews_level_2 == 2

    review_event = get_review_event(item.id, senior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 1
    assert item.in_progress_reviews_level_2 == 1

    review_event = get_review_event(item.id, senior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)

    assert item.in_progress_reviews_level_2 == 0
    assert item.open_reviews_level_2 == 3
    assert item.open_reviews == 3
    assert item.result_score == None


def get_review_event(item_id, user_id, score):
    review_event = {
        "body": {
            "item_id": item_id,
            "review_answers": [
                {
                    "review_question_id": "1",
                    "answer": score
                },
                {
                    "review_question_id": "2",
                    "answer": score
                },
                {
                    "review_question_id": "3",
                    "answer": score
                },
                {
                    "review_question_id": "4",
                    "answer": score
                },
                {
                    "review_question_id": "5",
                    "answer": score
                },
                {
                    "review_question_id": "6",
                    "answer": score
                },
                {
                    "review_question_id": "7",
                    "answer": score
                },
                {
                    "review_question_id": "8",
                    "answer": score
                },
                {
                    "review_question_id": "9",
                    "answer": score
                },
                {
                    "review_question_id": "10",
                    "answer": score
                },
                {
                    "review_question_id": "11",
                    "answer": score
                },
                {
                    "review_question_id": "12",
                    "answer": score
                },
                {
                    "review_question_id": "13",
                    "answer": score
                }
            ]
        },
        "requestContext": {
            "identity": {
                "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(user_id)
            }
        }
    }
    return review_event
