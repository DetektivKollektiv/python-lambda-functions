from core_layer.db_handler import Session
from core_layer.model.item_model import Item
from ml_service import GetTags
from core_layer.handler import item_handler
import json
import os

from archive_service.get_closed_items import get_closed_items

def test_get_closed_items():

    # pre-stuff
    os.environ["STAGE"] = "dev"

    with Session() as session:

        context = None

        # create item
        item = Item()
        item.content = "Test content"
        item.language = "de"
        item.status = "closed"
        item = item_handler.create_item(item, session)

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
        GetTags.post_tags_for_item(event1, context)
        GetTags.post_tags_for_item(event2, context)
        GetTags.post_tags_for_item(event3, context)

        # Check if tags are sorted by number of mentions
        response = get_closed_items(event1, context)
        body = response['body']
        tags = json.loads(body)[0]['tags']
        assert tags in [['B', 'C', 'A', 'D'], ['B', 'C', 'D', 'A']]
