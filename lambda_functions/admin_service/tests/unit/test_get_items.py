import pytest
import json
from uuid import uuid4
from sqlalchemy.orm import Session

from core_layer.model import Item
from core_layer.connection_handler import get_db_session
from ...get_items import get_items


@pytest.fixture
def item1():
    item = Item()
    item.id = str(uuid4())
    return item


@pytest.fixture
def item2():
    item = Item()
    item.id = str(uuid4())
    item.status = 'open'
    return item


@pytest.fixture
def session(item1, item2):
    session = get_db_session(True, None)
    session.add(item1)
    session.add(item2)
    session.commit()
    return session


def get_event(attribute, value):
    return {
        'queryStringParameters': {
            attribute: value
        }
    }


def test_get_items(session):
    event = {}
    response_body = json.loads(get_items(event, None, True, session)['body'])
    assert len(response_body) == 2

    event = get_event('status', 'open')
    response_body = json.loads(get_items(event, None, True, session)['body'])
    assert len(response_body) == 1

    event = get_event('NotAnAttribute', 'open')
    response = get_items(event, None, True, session)
    assert response['statusCode'] == 400
