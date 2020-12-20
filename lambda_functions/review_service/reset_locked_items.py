import logging
import traceback
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import review_handler


def reset_locked_items(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Reset locked items", event, logger)

    if session == None:
        session = get_db_session(False, None)

    try:
        reviews_in_progress = review_handler.get_old_reviews_in_progress(
            is_test, session)
        review_handler.delete_old_reviews_in_progress(
            reviews_in_progress, is_test, session)
        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": "Items updated"
        }
    except Exception:
        return {
            "statusCode": 400,
            "body": "Something went wrong. Check HTTP POST payload. Stacktrace: {}".format(traceback.format_exc())
        }
