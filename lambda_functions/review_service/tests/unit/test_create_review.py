import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from review_service import create_review
from core_layer.model.item_model import Item
from core_layer.model.review_model import Review
from core_layer.model.review_question_model import ReviewQuestion
from ....tests.helper import event_creator, setup_scenarios
from core_layer.test.helper.fixtures import database_fixture


@pytest.fixture
def item_id():
    return str(uuid4())


@pytest.fixture
def junior_user_id():
    return "1"


@pytest.fixture
def senior_user_id():
    return "11"


def test_bad_request():
    with Session() as session:
        event = {}
        response = create_review.create_review(event, None)
        assert response['statusCode'] == 400


def test_no_item_found(junior_user_id, database_fixture):
    with Session() as session:
        event = event_creator.get_create_review_event(junior_user_id, "wrong_item")
        response = create_review.create_review(event, None)
        assert response['statusCode'] == 404


def test_create_review(item_id, junior_user_id, senior_user_id, database_fixture):

    with Session() as session:

        session = setup_scenarios.create_questions(session)
        session = setup_scenarios.create_levels_junior_and_senior_detectives(session)
        item = Item(id=item_id, item_type_id="Type1")
        session.add(item)
        session.commit()        

        # Create junior review
        event = event_creator.get_create_review_event(junior_user_id, item_id)
        response = create_review.create_review(event, None)
        assert response['statusCode'] == 201
        reviews = session.query(Review).all()
        assert len(reviews) == 1
        review = Review()
        review = reviews[0]
        assert review.user_id == junior_user_id
        assert review.item_id == item_id
        question_ids = []
        for answer in review.review_answers:
            question_ids.append(answer.review_question_id)

        assert "other_type" not in question_ids
        parent_question_counter = 0
        for answer in review.review_answers:
            if answer.review_question.max_children > 0:
                child_questions = session.query(ReviewQuestion).filter(
                    ReviewQuestion.parent_question_id == answer.review_question_id).all()
                for child_question in child_questions:
                    assert child_question.id in question_ids
            if answer.review_question.parent_question_id is None:
                parent_question_counter += 1

        assert parent_question_counter == 6

        event = event_creator.get_create_review_event(senior_user_id, item_id)
        response = create_review.create_review(event, None)
        assert response['statusCode'] == 201
        reviews = session.query(Review).all()
        assert len(reviews) == 2
        reviews = session.query(Review).filter(
            Review.user_id == senior_user_id).all()
        assert len(reviews) == 1
        review = reviews[0]
        assert review.user_id == senior_user_id
        assert review.item_id == item_id
        for answer in review.review_answers:
            assert answer.review_question_id in question_ids
