import uuid
import pytest
from uuid import uuid4
from core_layer.connection_handler import get_db_session
from core_layer.model.comment_model import Comment
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from datetime import datetime

from sqlalchemy.sql.expression import null


@pytest.fixture
def event():
    return {
        "body": {
            "item_id": "test_item_id",
            "user_id": "test_user_id",
            "qualitative_comment": "Test comment"
        }
    }


@pytest.fixture
def item_id():
    return str(uuid4())


@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def session(item_id, user_id):
    session = get_db_session(True, None)

    item_obj = Item(id=item_id)
    user_obj = User(id=user_id)
    level_1_obj = Level(id=1)
    session.add_all([item_obj, level_1_obj, user_obj])
    session.commit()
    return session


def test_comment_model(event, item_id, user_id, session):

    body = event['body']
    # Save qualitative_comment
    comments_obj = Comment(id=str(uuid4()),
                           user_id=user_id,
                           comment=body['qualitative_comment'],
                           item_id=item_id
                           )
    session.add(comments_obj)
    session.commit()

    # Test comments
    comments = session.query(Comment).all()[0]
    assert comments.comment == 'Test comment'
    assert comments.item_id == item_id
    assert comments.user_id == user_id
