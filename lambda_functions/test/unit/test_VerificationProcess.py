import crud.operations as operations
from crud.model import User, Item
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker


def test_verification_process(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)

    # Creating six users
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

    senior_detective1 = User()
    senior_detective1.id = "11"
    senior_detective1.name = "Senior1"
    operations.create_user_db(senior_detective1, True, session)

    senior_detective2 = User()
    senior_detective2.id = "12"
    senior_detective2.name = "Senior2"
    operations.create_user_db(senior_detective2, True, session)

    senior_detective3 = User()
    senior_detective3.id = "13"
    senior_detective3.name = "Senior3"
    operations.create_user_db(senior_detective3, True, session)

    senior_detective4 = User()
    senior_detective4.id = "14"
    senior_detective4.name = "Senior4"
    operations.create_user_db(senior_detective3, True, session)

    users = operations.get_all_users_db(True, session)
    assert len(users) == 8

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item = operations.create_item_db(item, True, session)

    items = operations.get_all_items_db(True, session)
    assert len(items) == 1

    # Junior detective accepting item
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

    try:
        operations.accept_item_db(junior_detective4, item, True, session)
        assert True == False
    except:
        assert True == True

    # # Junior detective reviewing item
    # review_event = get_review_event(False, item.id, junior_detective1.id, 1)
    # app.submit_review(review_event, None, True, session)

    # item = operations.get_item_by_id(item.id, True, session)
    # assert item.status == "needs_senior"

    # # Senior detective accepting item
    # operations.accept_item_db(senior_detective1, item, True, session)
    # item = operations.get_item_by_id(item.id, True, session)
    # assert item.status == "locked_by_senior"
    # assert item.locked_by_user == senior_detective1.id

    # # Senior detective reviewing item
    # review_event = get_review_event(True, item.id, senior_detective1.id, 1)
    # app.submit_review(review_event, None, True, session)

    # item = operations.get_item_by_id(item.id, True, session)
    # assert item.status == "needs_junior"
    # assert item.open_reviews == 2

    # # Junior detective accepting item
    # operations.accept_item_db(junior_detective2, item, True, session)
    # item = operations.get_item_by_id(item.id, True, session)
    # assert item.status == "locked_by_junior"
    # assert item.locked_by_user == junior_detective2.id

    # # Junior detective reviewing item
    # review_event = get_review_event(False, item.id, junior_detective2.id, 1)
    # app.submit_review(review_event, None, True, session)

    # item = operations.get_item_by_id(item.id, True, session)
    # assert item.status == "needs_senior"

    # # Senior detective accepting item
    # operations.accept_item_db(senior_detective2, item, True, session)
    # item = operations.get_item_by_id(item.id, True, session)
    # assert item.status == "locked_by_senior"
    # assert item.locked_by_user == senior_detective2.id

    # # Senior detective reviewing item
    # review_event = get_review_event(True, item.id, senior_detective2.id, 1)
    # app.submit_review(review_event, None, True, session)

    # item = operations.get_item_by_id(item.id, True, session)
    # assert item.status == "needs_junior"
    # assert item.open_reviews == 1


def get_review_event(is_peer_review, item_id, user_id, score):
    review_event = {
        "body": {
            "is_peer_review": is_peer_review,
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
