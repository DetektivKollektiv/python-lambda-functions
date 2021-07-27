import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from review_service import create_review
from review_service import update_review
from core_layer.model.item_model import Item
from core_layer.model.review_model import Review
from core_layer.model.comment_model import Comment
from ....tests.helper import event_creator, setup_scenarios


@pytest.fixture
def item_id():
    return str(uuid4())


@pytest.fixture
def junior_user_id():
    return "1"


@pytest.fixture
def senior_user_id():
    return "11"


def test_update_review(item_id, junior_user_id, senior_user_id):

    with Session() as session:

        session = setup_scenarios.create_questions(session)
        session = setup_scenarios.create_levels_junior_and_senior_detectives(
            session)
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

        # Test 403
        event = event_creator.get_review_event(
            review, item_id, "in progress", senior_user_id, 1)

        response = update_review.update_review(event, None)
        assert response['statusCode'] == 403

        # Test comments
        comments = session.query(Comment).all()[0]
        assert comments.comment == "Test comment"
        assert comments.item_id == item_id
        assert comments.user_id == senior_user_id
        assert comments.status == "published"
        assert comments.is_review_comment == True

        event = event_creator.get_review_event(
            review, item_id, "in progress", junior_user_id, 1)

        response = update_review.update_review(event, None)
        assert response['statusCode'] == 200
