import uuid
from core_layer.db_handler import Session
from core_layer.model import Item, ReviewQuestion, ReviewAnswer, Review, User, Level
from archive_service import get_item
import json
import os
from core_layer.model import comment_model
from core_layer.model.comment_model import Comment
import pytest
from uuid import uuid4


@pytest.fixture()
def item_id():
    return str(uuid4())


@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def review_id():
    return str(uuid4())


@pytest.fixture
def review_answer_id():
    return str(uuid4())


@pytest.fixture
def comment_id():
    return str(uuid4())


def get_event(item_id):
    return {
        'pathParameters': {
            'item_id': item_id
        }
    }


def test_get_closed_items(item_id, review_id, review_answer_id, user_id, comment_id):
    os.environ["STAGE"] = "dev"

    with Session() as session:

        item = Item(id=item_id)
        review = Review(id=review_id, item_id=item_id, user_id=user_id)
        review_question = ReviewQuestion(id='Question1')
        review_answer = ReviewAnswer(
            id=review_answer_id, review_id=review_id, review_question_id=review_question.id)
        user = User(id=user_id, name='User')
        level = Level(id=1, description='beginner')
        comment = Comment(id=comment_id, comment='testcomment',
                          is_review_comment=True, user_id=user_id, item_id=item_id)
        session.add_all([item, review, review_question,
                        review_answer, user, level, comment])
        session.commit()

        # Test no query param
        event = {}
        response = get_item.get_item(event, None)
        assert response['statusCode'] == 400

        # Test invalid item id
        event = get_event('Quatsch_mit_Soße')
        response = get_item.get_item(event, None)
        assert response['statusCode'] == 404

        event = get_event(item_id)
        response = get_item.get_item(event, None)
        assert response['statusCode'] == 403

        item.status = 'closed'
        session.merge(item)
        response = get_item.get_item(event, None)
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['id'] == item.id
