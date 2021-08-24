import logging
import json
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import comment_handler, item_handler


def post_comment_on_item(event, context=None):
    """
    Creates comment on item from archive
    """

    with Session() as session:

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        try:
            body = json.loads(event['body']) if isinstance(
                event['body'], str) else event['body']
        except:
            return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event)

        try:
            user_id = helper.cognito_id_from_event(event)
            body = json.loads(event['body']) if isinstance(
                event['body'], str) else event['body']
        except:
            return helper.get_text_response(400, "Malformed request. Could not read user_id from context data.", event)

        if 'item_id' not in body:
            return helper.get_text_response(400, "Malformed request. Please provide an item_id.", event)

        try:
            item = item_handler.get_item_by_id(body['item_id'], session)
        except:
            return helper.get_text_response(404, "Item not found", event)

        # Save qualitative_comment
        if 'comment' in body:
            try:
                comment_handler.create_comment(session,
                                               comment=body['comment'],
                                               user_id=user_id,
                                               parent_type='item',
                                               parent_id=item.id
                                               )
            except:
                return helper.get_text_response(404, "No qualitative comment found.", event)
