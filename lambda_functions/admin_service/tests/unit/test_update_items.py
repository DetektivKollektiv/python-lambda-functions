import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from core_layer.model import Item
from core_layer.connection_handler import get_db_session
from ...update_item import update_item


@pytest.fixture
def item():
    item = Item()
    item.id = str(uuid4())
    return item


@pytest.fixture
def session(item):
    session = get_db_session(True, None)
    session.add(item)
    session.commit()
    return session


def get_event(item_id, attribute, value):
    return {
        'pathParameters': {
            'item_id': item_id
        },
        'body': {
            attribute: value
        }
    }


def test_update_item(session, item):

    item = session.query(Item).one()
    assert item.status == 'unconfirmed'

    # good request
    event = get_event(item.id, 'status', 'open')
    response = update_item(event, None, True, session)
    item = session.query(Item).one()
    assert item.status == 'open'
    assert response['statusCode'] == 200

    # item does not exist
    event = get_event('NotAnItemId', 'status', 'open')
    response = update_item(event, None, True, session)
    assert response['statusCode'] == 404

    # bad request
    event = get_event(item.id, 'NotAnItemAttribute', 'open')
    response = update_item(event, None, True, session)
    item = session.query(Item).one()
    assert response['statusCode'] == 400
