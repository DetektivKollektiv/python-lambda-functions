import logging
import json
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import comment_handler, item_handler


def post_comment_on_item(event, context = None, is_test = False, session = None):
    """
    Creates comment on item from archive
    """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        body = json.loads(event['body']) if isinstance(
            event['body'], str) else event['body']
    except:
        return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event, is_test)

    if 'item_id' not in body:
        return helper.get_text_response(400, "Malformed request. Please provide an item_id.", event, is_test)

    try:
        item = item_handler.get_item_by_id(body['item_id'], is_test, session)
    except:
        return helper.get_text_response(404, "Item not found", event, is_test)


    # Save qualitative_comment
    if 'qualitative_comment' in body:
        try:
            comment_handler.create_comment(comment = body['qualitative_comment'],
                                           user_id = body['user_id'],
                                           parent_type = 'item',
                                           parent_id = item.id,
                                           session = session
                                           )
        except:
            return helper.get_text_response(404, "No qualitative comment found.", event, is_test)