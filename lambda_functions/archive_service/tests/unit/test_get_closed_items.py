from core_layer.db_handler import Session
from core_layer.model.item_model import Item
from core_layer.model.url_model import URL, ItemURL
from ml_service import GetTags
from core_layer.handler import item_handler
import json
import os
from datetime import date, datetime
from archive_service.get_closed_items import get_closed_items
from core_layer.test.helper.fixtures import database_fixture


def get_url_event(url):
    return {
        "queryStringParameters": {
            "url": url
        }
    }


def test_get_closed_items(database_fixture):

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


def test_get_items_by_url():
    os.environ["STAGE"] = "dev"
    with Session() as session:
        item = Item()
        item.content = "Test content"
        item.language = "de"
        item.status = "closed"
        item = item_handler.create_item(item, session)

        item2 = Item()
        item2.content = "Test content2"
        item2.language = "de"
        item2.status = "closed"
        item2 = item_handler.create_item(item2, session)

        url = URL()
        url.id = "url_id"
        url.url = "www.test.de/artikel1"

        item_url = ItemURL()
        item_url.id = "item_url_id"
        item_url.item_id = item.id
        item_url.url_id = url.id

        session.add_all([url, item_url])
        session.commit()

        # Testing get_items without url query param 204
        for event in [{}, {"queryStringParameters": None}]:
            response = get_closed_items(event, None)
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert len(body) == 2

        # Testing get_items with url query param 200
        for url in [url.url, url.url+'?queryparam=shouldbeignored']:
            response = get_closed_items(get_url_event(url), None)
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert len(body) == 1
            assert body[0]['id'] == item.id

        # Testing get_items with url query param 204 - no item with url
        for url in ['sinnloseUrl', 'www.test.de/artikel2', 'www.test.de']:
            response = get_closed_items(get_url_event(url), None)
            assert response['statusCode'] == 204

        # Testing get_items with url query param 204 - item not closed
        item.status = "open"
        session.merge(item)
        session.commit()
        response = get_closed_items(
            get_url_event("www.test.de/artikel1"), None)
        assert response['statusCode'] == 204
