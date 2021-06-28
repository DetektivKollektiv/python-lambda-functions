import pytest
from uuid import uuid4
from core_layer.connection_handler import get_db_session
from core_layer.model.comment_model import Comment
from datetime import datetime

@pytest.fixture
def event():
    return {
        "body": {
            "item_id": "test_item_id",
            "user_id": "test_user_id",
            "qualitative_comment": "Test comment"
        }
    }


def test_comment_model(event):

    session = get_db_session(True, None)
    body = event['body']
    # Save qualitative_comment
    comments_obj = Comment(id = str(uuid4()),
                           user_id = body['user_id'],
                           comment = body['qualitative_comment'],
                           item_id = body['item_id']
                           )
    session.add(comments_obj)
    session.commit()


    # Test comments
    # comments = session.query(Comment).all()[0]
    # assert comments.comment == 'qualitative_comment'
    # assert comments.item_id == 'test_item_id'
    # assert comments.user_id == 'test_user_id'