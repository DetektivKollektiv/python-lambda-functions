import logging
import traceback
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import review_handler


def reset_locked_items(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Reset locked items", event, logger)

    session = Session()

    try:
        reviews_in_progress = review_handler.get_old_reviews_in_progress(session)
        review_handler.delete_old_reviews_in_progress(reviews_in_progress, session)
        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": "{} Review(s) deleted".format(len(reviews_in_progress))
        }
    except Exception:
        return {
            "statusCode": 400,
            "body": "Something went wrong. Check HTTP POST payload. Stacktrace: {}".format(traceback.format_exc())
        }
