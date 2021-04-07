import pytest
from core_layer.connection_handler import get_db_session

from core_layer.model.user_model import User
from core_layer.model.item_model import Item
from core_layer.model.level_model import Level
from core_layer.model.review_model import Review
from core_layer.model.review_pair_model import ReviewPair
from core_layer.model.review_question_model import ReviewQuestion
from core_layer.model.review_answer_model import ReviewAnswer
from core_layer.model.submission_model import Submission

from core_layer.handler import user_handler, item_handler, review_handler, review_pair_handler, review_question_handler

from ..helper import event_creator, setup_scenarios

from ...review_service.create_review import create_review
from ...review_service.update_review import update_review
from uuid import uuid4
from moto import mock_ses
import boto3


@mock_ses
def test_verification_process_best_case(monkeypatch):
    monkeypatch.setenv("STAGE", "dev")
    monkeypatch.setenv("DBNAME", "Test")
    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="info@detektivkollektiv.org")

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
    senior_detective2 = user_handler.get_user_by_id("12", True, session)
    senior_detective3 = user_handler.get_user_by_id("13", True, session)
    senior_detective4 = user_handler.get_user_by_id("14", True, session)
    senior_detective5 = user_handler.get_user_by_id("15", True, session)

    users = user_handler.get_all_users(True, session)
    assert len(users) == 10

    # Creating an item

    item = Item()
    item.content = "This item needs to be checked"
    item.item_type_id = "Type1"
    item = item_handler.create_item(item, True, session)
    assert item.in_progress_reviews_level_1 == 0
    assert item.open_reviews_level_1 == 4
    assert item.status == 'unconfirmed'

    item.status = 'open'
    session.merge(item)

    submission = Submission()
    submission.id = 'Submission 1'
    submission.item_id = item.id
    submission.mail = 'test@test.de'
    submission.status = 'confirmed'
    session.add(submission)
    session.commit()

    items = item_handler.get_all_items(True, session)
    assert len(items) == 1

    # Junior detectives accepting item
    jr1 = review_handler.create_review(junior_detective1, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 1

    jr2 = review_handler.create_review(junior_detective2, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 2

    jr3 = review_handler.create_review(junior_detective3, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 3

    jr4 = review_handler.create_review(junior_detective4, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 4

    with pytest.raises(Exception):
        review_handler.create_review(junior_detective5, item, True, session)

    # Senior detectives accepting item
    sr1 = review_handler.create_review(senior_detective1, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 1

    sr2 = review_handler.create_review(senior_detective2, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 2

    sr3 = review_handler.create_review(senior_detective3, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 3

    sr4 = review_handler.create_review(senior_detective4, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 4

    with pytest.raises(Exception):
        review_handler.create_review(senior_detective5, item, True, session)

    pairs = review_pair_handler.get_review_pairs_by_item(
        item.id, True, session)
    assert len(pairs) == 4

    # Detectives reviewing item
    reviews = [jr1, jr2, jr3, jr4, sr1, sr2, sr3, sr4]
    for review in reviews:
        event = event_creator.get_review_event(
            review, item.id, "in progress", review.user_id, 1, session)
        response = update_review(event, None, True, session)
        assert response['statusCode'] == 200
        session.refresh(review)
        event = event_creator.get_review_event(
            review, item.id, "closed", review.user_id, 1, session)
        response = update_review(event, None, True, session)
        assert response['statusCode'] == 200

    assert item.status == 'closed'
    assert item.in_progress_reviews_level_1 == 0
    assert item.in_progress_reviews_level_2 == 0
    assert item.open_reviews_level_1 == 0
    assert item.open_reviews_level_2 == 0
    assert item.open_reviews == 0

    send_quota = conn.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 1
    session.refresh(submission)
    assert not submission.mail


def test_verification_process_worst_case(monkeypatch):

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
    senior_detective2 = user_handler.get_user_by_id("12", True, session)
    senior_detective3 = user_handler.get_user_by_id("13", True, session)
    senior_detective4 = user_handler.get_user_by_id("14", True, session)
    senior_detective5 = user_handler.get_user_by_id("15", True, session)

    users = user_handler.get_all_users(True, session)
    assert len(users) == 10

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item.status = 'open'
    item.item_type_id = "Type1"
    item = item_handler.create_item(item, True, session)

    items = item_handler.get_all_items(True, session)
    assert len(items) == 1

    # Junior detectives accepting item
    jr1 = review_handler.create_review(junior_detective1, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 1

    jr2 = review_handler.create_review(junior_detective2, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 2

    jr3 = review_handler.create_review(junior_detective3, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 3

    jr4 = review_handler.create_review(junior_detective4, item, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 4

    with pytest.raises(Exception):
        review_handler.create_review(junior_detective5, item, True, session)

    # Senior detectives accepting item
    sr1 = review_handler.create_review(senior_detective1, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 1

    sr2 = review_handler.create_review(senior_detective2, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 2

    sr3 = review_handler.create_review(senior_detective3, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 3

    sr4 = review_handler.create_review(senior_detective4, item, True, session)
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_2 == 4

    with pytest.raises(Exception):
        review_handler.create_review(senior_detective5, item, True, session)

    pairs = review_pair_handler.get_review_pairs_by_item(
        item.id, True, session)
    assert len(pairs) == 4

    # Detective without review in progress trying to get question
    junior_reviews = [jr1, jr2, jr3, jr4]
    senior_reviews = [sr1, sr2, sr3, sr4]
    for review in junior_reviews:
        event = event_creator.get_review_event(
            review, item.id, "in progress", review.user_id, 1, session)
        response = update_review(event, None, True, session)
        assert response['statusCode'] == 200
        session.refresh(review)
        event = event_creator.get_review_event(
            review, item.id, "closed", review.user_id, 1, session)
        response = update_review(event, None, True, session)
        assert response['statusCode'] == 200

    for review in senior_reviews:
        event = event_creator.get_review_event(
            review, item.id, "in progress", review.user_id, 4, session)
        response = update_review(event, None, True, session)
        assert response['statusCode'] == 200
        session.refresh(review)
        event = event_creator.get_review_event(
            review, item.id, "closed", review.user_id, 4, session)
        response = update_review(event, None, True, session)
        assert response['statusCode'] == 200

    assert item.status == 'open'
    assert item.in_progress_reviews_level_1 == 0
    assert item.in_progress_reviews_level_2 == 0
    assert item.open_reviews_level_1 == 4
    assert item.open_reviews_level_2 == 4
    assert item.open_reviews == 4


def test_create_review(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")

    session = get_db_session(True, None)
    session = setup_scenarios.create_levels_junior_and_senior_detectives(
        session)

    junior_detective1 = user_handler.get_user_by_id("1", True, session)
    junior_detective2 = user_handler.get_user_by_id("2", True, session)
    junior_detective3 = user_handler.get_user_by_id("3", True, session)
    junior_detective4 = user_handler.get_user_by_id("4", True, session)

    senior_detective1 = user_handler.get_user_by_id("11", True, session)
    senior_detective2 = user_handler.get_user_by_id("12", True, session)
    senior_detective3 = user_handler.get_user_by_id("13", True, session)
    senior_detective4 = user_handler.get_user_by_id("14", True, session)

    users = user_handler.get_all_users(True, session)
    assert len(users) == 10

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item = item_handler.create_item(item, True, session)

    items = item_handler.get_all_items(True, session)
    assert len(items) == 1

    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 0
    assert len(review_pairs) == 0

    # Junior detectives accepting item
    event = event_creator.get_create_review_event(
        junior_detective1.id, item.id)
    response = create_review(event, None, True, session)
    assert response['statusCode'] == 201
    item = item_handler.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 1
    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 1
    assert len(review_pairs) == 1

    event = event_creator.get_create_review_event(
        junior_detective2.id, item.id)
    create_review(event, None, True, session)
    item = item_handler.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_1 == 2
    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 2
    assert len(review_pairs) == 2

    # Senior detective accepting item
    event = event_creator.get_create_review_event(
        senior_detective1.id, item.id)
    create_review(event, None, True, session)
    item = item_handler.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 4
    assert item.in_progress_reviews_level_2 == 1
    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 3
    assert len(review_pairs) == 2
