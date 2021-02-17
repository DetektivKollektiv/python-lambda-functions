# External imports
import logging
import json
from uuid import uuid4
# Helper imports
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import item_handler, tag_handler
import EnrichItem


def get_tags_for_item(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get tags by item id", event, logger)

    if session is None:
        session = get_db_session(is_test, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        try:
            tag_objects = tag_handler.get_tags_by_itemid(id, is_test, session)

            tags = []
            for obj in tag_objects:
                tags.append(obj.to_dict()['tag'])
        except Exception as e:
            response = {
                "statusCode": 404,
                "body": "No tags found. Exception: {}".format(e)
            }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get item ID. Check HTTP GET payload. Exception: {}".format(e)
        }
    body_json = {"Tags": tags}
    response = {
        "statusCode": 200,
        'headers': {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps(body_json)
    }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors

def post_tags_for_item(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Post tags by item id", event, logger)

    if session is None:
        session = get_db_session(is_test, None)

    tags_existing = []
    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        tag_objects = tag_handler.get_tags_by_itemid(id, is_test, session)

        for obj in tag_objects:
            tags_existing.append(obj.to_dict()['tag'])
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get item ID. Check HTTP POST payload. Exception: {}".format(e)
        }

    body = event['body']

    if isinstance(body, str):
        body_dict = json.loads(body)
    else:
        body_dict = body
    if 'tags' in body_dict:
        tags_posted = body_dict['tags']
    else:
        tags_posted = []        

    tags_new = list(set(tags_posted)-set(tags_existing))
    if tags_new != []:
        for str_tag in tags_new:
            tag_handler.store_tag_for_item(id, str_tag, is_test, session)

    tags_removed = list(set(tags_existing)-set(tags_posted))
    for str_tag in tags_removed:
        # search for tag in database
        tag = tag_handler.get_tag_by_content(str_tag, is_test, session)
        if tag is not None:
            tag_handler.delete_itemtag_by_tag_and_item_id(tag.id, id, is_test, session)

    response = {
        "statusCode": 200,
        'headers': {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps({"added tags": tags_new,"removed tags": tags_removed})
    }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
