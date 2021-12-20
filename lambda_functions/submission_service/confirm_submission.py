import os
import io
import logging
import traceback
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import submission_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def confirm_submission(event, context):

    helper.log_method_initiated("Confirm submission", event, logger)

    submission_id = event['pathParameters']['submission_id']

    stage = os.environ['STAGE']
    if stage == 'prod':
        link = 'https://codetekt.org'
    else:
        link = 'https://{}.codetekt.org'.format(stage)

    body_html = io.open(os.path.join(os.path.dirname(__file__), 'resources',
                                     'submission_confirmed_webpage.html'), mode='r', encoding='utf-8').read().format(link)

    with Session() as session:                                 

        try:
            submission_handler.confirm_submission(submission_id, session)
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

        return helper.set_cors(response, event)
