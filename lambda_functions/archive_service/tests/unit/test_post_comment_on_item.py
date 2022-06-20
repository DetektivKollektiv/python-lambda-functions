import json
import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from archive_service.post_comment_on_item import post_comment_on_item
from core_layer.test.helper.fixtures import database_fixture


@pytest.fixture
def item_id():
    return str(uuid4())


@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def event(item_id, user_id):
    return {
        "requestContext": {
            "identity": {
                "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(user_id)
            }
        },
        "body": {
            "item_id": item_id,
            "comment": "Comment from event"
        }
    }


def test_post_comment_on_item(event, item_id, user_id, database_fixture):

    with Session() as session:

        item_obj = Item(id=item_id)
        user_obj = User(id=user_id, name='Testuser')
        level_1_obj = Level(id=1)
        session.add_all([item_obj, level_1_obj, user_obj])
        session.commit()

        response = post_comment_on_item(event)

        body = json.loads(response['body'])
        assert body['user'] == 'Testuser'

        comment = session.query(Item).all()[
            0].comments[0]

        assert comment.comment == "Comment from event"
        assert comment.is_review_comment == False
        assert comment.status == "published"
