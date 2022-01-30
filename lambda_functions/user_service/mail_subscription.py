import os
import io
import logging
import traceback
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import user_handler, mail_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def confirm_mail_subscription(event):

    helper.log_method_initiated("Confirm mail subscription", event, logger)

    mail_id = event['pathParameters']['mail_id']

    stage = os.environ['STAGE']
    if stage == 'prod':
        link = 'https://codetekt.org'
    else:
        link = 'https://{}.codetekt.org'.format(stage)

    body_html = io.open(os.path.join(os.path.dirname(__file__), 'resources',
                                     'mail_confirmed_webpage.html'), mode='r', encoding='utf-8').read().format(link)

    with Session() as session:                                 

        try:
            user_handler.confirm_mail_subscription(mail_id, session)
            response = {
                'statusCode': 200,
                'headers': {"content-type": "text/html; charset=utf-8"},
                'body': body_html
            }

        except Exception:
            response = {
                "statusCode": 500,
                "body": "Could not unsubscribe mail. Stacktrace: {}".format(traceback.format_exc())
            }

        return helper.set_cors(response, event)


def unsubscribe_mail(event):

    helper.log_method_initiated("Unsubscribe mail", event, logger)

    mail_id = event['pathParameters']['mail_id']

    stage = os.environ['STAGE']
    if stage == 'prod':
        link = 'https://codetekt.org'
    else:
        link = 'https://{}.codetekt.org'.format(stage)

    body_html = io.open(os.path.join(os.path.dirname(__file__), 'resources',
                                     'mail_unsubscribed_webpage.html'), mode='r', encoding='utf-8').read().format(link)

    with Session() as session:                                 

        try:
            user_handler.unsubscribe_mail(mail_id, session)
            response = {
                'statusCode': 200,
                'headers': {"content-type": "text/html; charset=utf-8"},
                'body': body_html
            }

        except Exception:
            response = {
                "statusCode": 500,
                "body": "Could not unsubscribe mail. Stacktrace: {}".format(traceback.format_exc())
            }

        return helper.set_cors(response, event)