from core_layer.connection_handler import get_db_session
from core_layer.model.item_model import Item
from ml_service import GetTags
from core_layer.handler import item_handler
import json
import pytest
import os

from archive_service.get_closed_items import get_closed_items

def test_get_closed_items(monkeypatch):

    # pre-stuff
    monkeypatch.setenv("DBNAME", "Test")
    os.environ["STAGE"] = "dev"
    session = get_db_session(True, None)
    context = None

    # create item
    item = Item()
    item.content = "Test content"
    item.language = "de"
    item.status = "closed"
    item = item_handler.create_item(item, True, session)

    # create events with tags
    event1 = {
        "pathParameters": {
            "item_id": item.id
        },
        "body": json.dumps({"tags": ['C', 'B', 'D']})
    }
    event2 = {
        "pathParameters": {
            "item_id": item.id
        },
        "body": json.dumps({"tags": ['B', 'C']})
    }
    event3 = {
        "pathParameters": {
            "item_id": item.id
        },
        "body": json.dumps({"tags": ['A', 'B']})
    }

    # post tags
    GetTags.post_tags_for_item(event1, context, True, session)
    GetTags.post_tags_for_item(event2, context, True, session)
    GetTags.post_tags_for_item(event3, context, True, session)

    # Check if tags are sorted by number of mentions
    response = get_closed_items(event1, context, True, session)
    body = response['body']
    tags = json.loads(body)[0]['tags']
    assert tags == ['B', 'C', 'D', 'A']