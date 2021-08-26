from core_layer.db_handler import Session
from core_layer.model.review_answer_model import ReviewAnswer
import pytest
import json
from uuid import uuid4
from core_layer.model import Item, User, Review, ReviewQuestion, Level, Comment


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


def test_item_model_to_dict_with_reviews(item_id, review_id, review_answer_id, user_id, comment_id):
    with Session() as session:
        item = Item(id=item_id)
        review = Review(id=review_id, item_id=item_id, user_id=user_id)
        review_question = ReviewQuestion(id='Question1')
        review_answer = ReviewAnswer(
            id=review_answer_id, review_id=review_id, review_question_id=review_question.id)
        user = User(id=user_id, name='testuser')
        level = Level(id=1)
        comment = Comment(id=comment_id, comment='testcomment',
                          is_review_comment=True, user_id=user_id, item_id=item_id)
        session.add_all([item, review, review_question,
                        review_answer, user, level, comment])
        session.commit()

        assert len(item.reviews) == 1
        assert item.reviews[0].id == review_id

        item_dict = item.to_dict(with_reviews=True, with_comments=True)
        assert item_dict['reviews']
        assert len(item_dict['reviews']) == 1
        assert item_dict['reviews'][0]['id'] == review_id
        assert item_dict['reviews'][0]['user'] == user.name
        assert len(item_dict['reviews'][0]['questions']) == 1
        assert 'comments' in item_dict
        assert len(item_dict['comments']) == 1
        assert item_dict['comments'][0]['comment'] == 'testcomment'
        assert item_dict['comments'][0]['user'] == user.name

        session.delete(user)
        session.expire_all()
        item_dict = item.to_dict(with_reviews=True, with_comments=True)
        assert item_dict['comments'][0]['user'] == 'deleted'
        assert item_dict['reviews'][0]['user'] == 'deleted'
