import pytest
from uuid import uuid4
from core_layer.connection_handler import get_db_session
from core_layer.model.comment_model import Comment, CommentSentiment
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.model.submission_model import Submission
from core_layer.model.issue_model import Issue


@pytest.fixture
def item_id():
    return str(uuid4())

@pytest.fixture
def submission_id():
    return str(uuid4())

@pytest.fixture
def existing_comment_id():
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
            "qualitative_comment": "Comment from event"
        }
    }

@pytest.fixture
def session(item_id, user1_id, user2_id, submission_id):
    session = get_db_session(True, None)

    item_obj = Item(id = item_id)
    user1_obj = User(id = user1_id)
    user2_obj = User(id = user2_id)
    level_1_obj = Level(id = 1)
    submission_obj = Submission(id = submission_id)
    session.add_all([item_obj, level_1_obj, user1_obj, user2_obj, submission_obj])
    session.commit()
    return session


def test_comment_model(event, item_id, user1_id, user2_id, session, submission_id, existing_comment_id):


    """
    Test comment on item
    """
    body = event['body']
    # Save qualitative_comment
    comments_obj_on_item = Comment(id = existing_comment_id,
                                   user_id = user1_id,
                                   comment = body['qualitative_comment'],
                                   item_id = item_id
                                  )
    session.add(comments_obj_on_item)
    session.commit()
    # Asserts
    comment_on_item = session.query(Comment).filter(Comment.item_id.isnot(None)).first()
    assert comment_on_item.comment == 'Comment from event'
    assert comment_on_item.item_id == item_id
    assert comment_on_item.user_id == user1_id
    assert comment_on_item.status == 'published'
    assert session.query(Item).first().comments[0].comment == 'Comment from event'


    """
    Test comment on submission
    """
    # Save qualitative_comment
    comment_obj_on_submission = Comment(id = str(uuid4()),
                                        user_id = user1_id,
                                        comment = 'Comment on submission',
                                        submission_id = submission_id
                                       )
    session.add(comment_obj_on_submission)
    session.commit()
    # Asserts
    comment_on_submission = session.query(Comment).filter(Comment.submission_id.isnot(None)).first()
    assert comment_on_submission.comment == 'Comment on submission'
    assert comment_on_submission.submission_id == submission_id
    assert comment_on_submission.user_id == user1_id
    assert session.query(Submission).first().comments[0].comment == 'Comment on submission'


    """
    Test comment on comment
    """
    # Save qualitative_comment on first comment ('Comment from event')
    comment_obj_on_comment = Comment(id = str(uuid4()),
                                     user_id = user2_id,
                                     comment = 'Comment on comment',
                                     parent_comment_id = existing_comment_id
                                    )
    session.add(comment_obj_on_comment)
    session.commit()
    # Asserts
    comment_on_comment = session.query(Comment).filter(Comment.parent_comment_id.isnot(None)).first()
    assert comment_on_comment.comment == 'Comment on comment'
    assert comment_on_comment.parent_comment_id == existing_comment_id
    assert comment_on_comment.user_id == user2_id
    assert comment_on_comment.parent_comment.comment == 'Comment from event'


    """
    Test comment sentiment
    """
    # Save sentiment on on first comment ('Comment from event')
    sentiment_obj = CommentSentiment(id = str(uuid4()),
                                     type = 'like',
                                     user_id = user2_id,
                                     comment_id = existing_comment_id
                                    )
    session.add(sentiment_obj)
    session.commit()   
    sentiment = session.query(CommentSentiment).first()
    assert sentiment.type == 'like'
    assert sentiment.user_id == user2_id
    assert sentiment.comment_id == existing_comment_id
    assert session.query(Comment).first().comment_sentiments[0].type == 'like'


    """
    Test issue about comment
    """
    # Save issue on on first comment ('Comment from event')
    issue_obj = Issue(category = 'Beleidigung',
                      message = 'der hat mich Blödmann genannt',
                      comment_id = existing_comment_id
                     )
    session.add(issue_obj)
    session.commit()
    issue = session.query(Issue)
    assert issue.count() == 1
    assert len(session.query(Comment).first().issues) == 1
    assert session.query(Issue).first().comment.comment == 'Comment from event'