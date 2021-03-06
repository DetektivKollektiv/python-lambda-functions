import os
import io
import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import submission_handler
from core_layer.model import Submission

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def confirm_submission(event, context, is_test=False, session=None):

    helper.log_method_initiated("Confirm submission", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    submission_id = event['pathParameters']['submission_id']

    stage = os.environ['STAGE']
    if stage == 'prod':
        link = 'https://codetekt.org'
    else:
        link = 'https://{}.codetekt.org'.format(stage)

    body_html = io.open(os.path.join(os.path.dirname(__file__), 'resources',
                                     'submission_confirmed_webpage.html'), mode='r', encoding='utf-8').read().format(link)

    try:
        submission_handler.confirm_submission(
            submission_id, is_test, session)
        response = {
            'statusCode': 200,
            'headers': {"content-type": "text/html; charset=utf-8"},
            'body': body_html
        }

    except Exception:
        response = {
            "statusCode": 500,
            "body": "Could not confirm submission. Stacktrace: {}".format(traceback.format_exc())
        }

    return helper.set_cors(response, event, is_test)
