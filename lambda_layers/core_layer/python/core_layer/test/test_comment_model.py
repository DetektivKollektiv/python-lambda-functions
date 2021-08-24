import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from core_layer.model.comment_model import Comment, CommentSentiment
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.model.submission_model import Submission
from core_layer.model.issue_model import Issue
from core_layer.handler import comment_handler


@pytest.fixture
def item_id():
    return str(uuid4())


@pytest.fixture
def submission_id():
    return str(uuid4())


@pytest.fixture
def user1_id():
    return str(uuid4())


@pytest.fixture
def user2_id():
    return str(uuid4())


@pytest.fixture
def event(user2_id):
    return {
        "body": {
            "user_id": user2_id,
            "comment": "Comment from event"
        }
    }


def test_comment_model(event, item_id, user1_id, user2_id, submission_id):

    with Session() as session:

        item_obj = Item(id=item_id)
        user1_obj = User(id=user1_id)
        user2_obj = User(id=user2_id)
        level_1_obj = Level(id=1)
        submission_obj = Submission(id=submission_id)
        session.add_all([item_obj, level_1_obj, user1_obj,
                        user2_obj, submission_obj])
        session.commit()

        """
        Test comment on item
        """
        body = event['body']
        # Save qualitative_comment
        comment_handler.create_comment(session,
                                       comment=body['comment'],
                                       user_id=user1_id,
                                       parent_type='item',
                                       parent_id=item_id
                                       )
        # Asserts
        comment_on_item = session.query(Comment).filter(
            Comment.item_id.isnot(None)).first()
        assert comment_on_item.comment == 'Comment from event'
        assert comment_on_item.item_id == item_id
        assert comment_on_item.user_id == user1_id
        assert comment_on_item.status == 'published'
        assert session.query(Item).first(
        ).comments[0].comment == 'Comment from event'

        """
        Test comment on submission
        """
        # Save qualitative_comment
        comment_handler.create_comment(session,
                                       comment='Comment on submission',
                                       user_id=user1_id,
                                       parent_type='submission',
                                       parent_id=submission_id
                                       )
        # Asserts
        comment_on_submission = session.query(Comment).filter(
            Comment.submission_id.isnot(None)).first()
        assert comment_on_submission.comment == 'Comment on submission'
        assert comment_on_submission.submission_id == submission_id
        assert comment_on_submission.user_id == user1_id
        assert session.query(Submission).first(
        ).comments[0].comment == 'Comment on submission'

        """
        Test comment on comment
        """
        # Save qualitative_comment on first comment ('Comment from event')
        first_comment_id = session.query(Comment).first().id
        comment_handler.create_comment(session,
                                       comment='Comment on comment',
                                       user_id=user2_id,
                                       parent_type='comment',
                                       parent_id=first_comment_id
                                       )
        # Asserts
        comment_on_comment = session.query(Comment).filter(
            Comment.parent_comment_id.isnot(None)).first()
        assert comment_on_comment.comment == 'Comment on comment'
        assert comment_on_comment.parent_comment_id == first_comment_id
        assert comment_on_comment.user_id == user2_id
        assert comment_on_comment.parent_comment.comment == 'Comment from event'

        """
        Test comment sentiment
        """
        # Save sentiment on on first comment ('Comment from event')
        sentiment_obj = CommentSentiment(id=str(uuid4()),
                                         type='like',
                                         user_id=user2_id,
                                         comment_id=first_comment_id
                                         )
        session.add(sentiment_obj)
        session.commit()
        sentiment = session.query(CommentSentiment).first()
        assert sentiment.type == 'like'
        assert sentiment.user_id == user2_id
        assert sentiment.comment_id == first_comment_id
        assert session.query(Comment).first(
        ).comment_sentiments[0].type == 'like'

        """
        Test issue about comment
        """
        # Create issue on on first comment ('Comment from event')
        issue_obj = Issue(category='Beleidigung',
                          message='der hat mich Blödmann genannt',
                          comment_id=first_comment_id
                          )
        session.add(issue_obj)
        session.commit()
        issue = session.query(Issue)
        assert issue.count() == 1
        assert len(session.query(Comment).first().issues) == 1
        assert session.query(Issue).first(
        ).comment.comment == 'Comment from event'
