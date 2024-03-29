import pytest
import json
from uuid import uuid4
from core_layer.db_handler import Session

from core_layer.model import Item, ItemType
from ...get_items import get_items



@pytest.fixture
def test_item_type():
    item_type = ItemType()
    item_type.id = str(uuid4())
    item_type.name = "test"
    return item_type


@pytest.fixture
def item1(test_item_type: ItemType):
    item = Item()
    item.id = str(uuid4())
    item.item_type_id = test_item_type.id
    return item


@pytest.fixture
def item2(test_item_type: ItemType):
    item = Item()
    item.id = str(uuid4())
    item.status = 'open'
    item.item_type_id = test_item_type.id
    return item


@pytest.fixture
def item_with_type(test_item_type: ItemType):
    item = Item()
    item.id = str(uuid4())
    item.status = 'open'
    item.item_type_id = test_item_type.id
    return item


def get_event(attribute, value):
    return {
        'queryStringParameters': {
            attribute: value
        }
    }


def test_get_items(test_item_type, item1, item2, item_with_type):
    
    with Session() as session:
        
        session.add(test_item_type)
        session.add(item1)
        session.add(item2)
        session.add(item_with_type)
        session.commit()
        
        event = {}
        response_body = json.loads(get_items(event, None)['body'])
        assert len(response_body) == 3
        assert all('test' in i['item_type']['name'] for i in response_body)

        event = {'queryStringParameters': None}
        response_body = json.loads(get_items(event, None)['body'])
        assert len(response_body) == 3
        assert all('test' in i['item_type']['name'] for i in response_body)

        event = get_event('status', 'open')
        response_body = json.loads(get_items(event, None)['body'])
        assert len(response_body) == 2
        assert all('test' in i['item_type']['name'] for i in response_body)

        event = get_event('NotAnAttribute', 'open')
        response = get_items(event, None)
        assert response['statusCode'] == 400
