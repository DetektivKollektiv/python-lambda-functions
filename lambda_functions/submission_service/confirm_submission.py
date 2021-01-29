import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import submission_handler
from core_layer.model import Submission


def confirm_submission(event, context, is_test=False, session=None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Confirm submission", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    submission_id = event['pathParameters']['submission_id']

    try:
        submission = Submission()
        submission = submission_handler.confirm_submission(
            submission_id, is_test, session)
        response = {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(submission.to_dict())
        }

    except Exception:
        response = {
            "statusCode": 500,
            "body": "Could not confirm submission. Stacktrace: {}".format(traceback.format_exc())
        }

    return helper.set_cors(response, event, is_test)
