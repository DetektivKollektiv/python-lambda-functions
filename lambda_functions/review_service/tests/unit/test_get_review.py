import pytest
import json

from core_layer.model.review_question_model import ReviewQuestion
from core_layer.model.review_answer_model import ReviewAnswer, AnswerOption
from core_layer.model.review_model import Review
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.model.tag_model import Tag, ItemTag
from core_layer.model.comment_model import Comment

from review_service.get_review import get_review

from ....tests.helper import event_creator
from core_layer.db_handler import Session

from uuid import uuid4


@pytest.fixture
def item_id():
    return str(uuid4())


@pytest.fixture
def review_id():
    return str(uuid4())


@pytest.fixture
def review_question_id():
    return str(uuid4())


@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def tag_id():
    return str(uuid4())


@pytest.fixture
def item_tag_id():
    return str(uuid4())


def generate_review_answer(answer, review_id, review_question_id):
    return ReviewAnswer(id=str(uuid4()), review_id=review_id, review_question_id=review_question_id, answer=answer, comment='Test Review Answer')


def test_get_review(item_id, review_id, review_question_id, user_id, tag_id, item_tag_id, monkeypatch):
    """
    Gets a simple Review
    """
    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:4200")

    with Session() as session:

        item = Item()
        item.id = item_id

        user = User()
        user.id = user_id

        level = Level(id=1)

        review = Review()
        review.id = review_id
        review.item_id = item.id
        review.user_id = user.id
        review.status = 'in_progress'

        tag = Tag(tag='test', id=tag_id)
        item_tag = ItemTag(id=item_tag_id, item_id=item_id,
                           tag_id=tag_id, review_id=review_id)

        comment = Comment(id='comment_id', comment='testcomment',
                          review_id=review_id, is_review_comment=True)

        review_question = ReviewQuestion()
        review_question.id = review_question_id
        review_question.content = "Question content"
        review_question.info = "Question info"
        review_question.hint = "Question hint"

        o1 = AnswerOption(id="1", text="Option 1", value=0)
        o2 = AnswerOption(id="2", text="Option 2",
                          value=1, tooltip="Tooltip 2")
        o3 = AnswerOption(id="3", text="Option 3", value=2)
        o4 = AnswerOption(id="4", text="Option 4", value=3)

        o1.questions = [review_question]
        o2.questions = [review_question]
        o4.questions = [review_question]
        o3.questions = [review_question]

        # all answers use the same review questions in order to keep the test data small
        reviewanswer1 = generate_review_answer(
            1, review_id, review_question_id)
        reviewanswer2 = generate_review_answer(
            0, review_id, review_question_id)
        reviewanswer3 = generate_review_answer(
            1, review_id, review_question_id)
        reviewanswer4 = generate_review_answer(
            3, review_id, review_question_id)
        reviewanswer5 = generate_review_answer(
            2, review_id, review_question_id)
        reviewanswer6 = generate_review_answer(
            1, review_id, review_question_id)
        reviewanswer7 = generate_review_answer(
            2, review_id, review_question_id)
        review.review_answers = [reviewanswer1, reviewanswer2, reviewanswer3,
                                 reviewanswer4, reviewanswer5, reviewanswer6, reviewanswer7]

        session.add(item)
        session.add(user)
        session.add(level)
        session.add(review_question)
        session.add_all([tag, item_tag, comment])
        # referenced ReviewAnswers are stored as well
        session.add(review)

        session.commit()

        event = event_creator.get_get_review_event(user_id, review_id)

        resp = get_review(event, None)

        status = resp["statusCode"]
        assert status == 200

        body = json.loads(resp["body"])
        assert body["id"] == review_id

        assert len(body["questions"]) == 7
        assert body["questions"][0]["answer_id"] != None
        assert body["questions"][0]["question_id"] != None
        assert body["questions"][0]["parent_question_id"] == None
        assert body["questions"][0]["max_children"] == None
        assert body["questions"][0]["content"] != None
        assert body["questions"][0]["info"] != None
        assert body["questions"][0]["hint"] != None
        assert body["questions"][0]["answer_value"] == 1
        assert len(body["questions"][0]["options"]) == 4
        assert body["questions"][0]["options"][0]["text"] != None
        assert body["questions"][0]["options"][0]["value"] == 0
        assert body["questions"][0]["options"][1]["tooltip"] != None

        assert 'tags' in body
        assert len(body['tags']) == 1
        assert body['tags'][0] == 'test'

        assert 'comment' in body
        assert body['comment'] == 'testcomment'
