import logging
import traceback
import json

import boto3
from botocore.exceptions import ClientError

from core_layer.connection_handler import add_object, get_db_session
from core_layer import helper
from core_layer.model.issue_model import Issue

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def submit_issue(event, context, is_test=False, session=None):

    helper.log_method_initiated("Submit issue", event, logger)

    if session == None:
        session = get_db_session(is_test, session)

    issue = Issue() #create object from issue_model.py (DB table: issues)
    issue = helper.body_to_object(event['body'], issue) 
    # add ip address
    try:
        ip_address = event['requestContext']['identity']['sourceIp']
        setattr(issue, 'ip_address', ip_address)
    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not read/add ip address. Check HTTP POST payload. Stacktrace: {}".format(traceback.format_exc())
        }        

    issue = add_object(issue, is_test, session)
    if issue is None:
        response = {
            "statusCode": 400,
            "body": "Could not write issue to database. Check HTTP POST payload. Stacktrace: {}".format(traceback.format_exc())
        }
        response_cors = helper.set_cors(response, event, is_test)
        return response_cors

    response = send_issue_notification(issue)
    if response == False:
        response = {
            "statusCode": 500,
            "body": "Could not send issue mail. Stacktrace: {}".format(traceback.format_exc())
        }
        response_cors = helper.set_cors(response, event, is_test)
        return response_cors

    else:
        response = {
            "statusCode": 201,
            "body": json.dumps(issue.to_dict())
        }
        response_cors = helper.set_cors(response, event, is_test)
        return response_cors


def send_issue_notification(issue: Issue) -> bool:
    mail_adress = 'info@detektivkollektiv.org'
    aws_region = 'eu-central-1'
    subject = 'Eine Nutzer*in hat das Kontaktformular ausgefüllt'
    body_text = '''Eine Nutzer*in hat das Kontaktformular ausgefüllt! \n
    Kategorie: {} \n 
    Nachricht: {} {}
    '''

    body_html = '''<html>
    <head><title>Eine Nutzer*in hat das Kontaktformular ausgefüllt!</title></head>
    <body>    
    <h1 style="color: #ffcc00;">Kategorie:</h1>
    <p>{}</p>
    <h1 style="color: #ffcc00;">Nachricht:</h1>
    <p>{}</p>
    {}
    </body>
    </html>
    '''

    if issue.item_id is None:
        body_text = body_text.format(issue.category, issue.message, '')
        body_html = body_html.format(issue.category, issue.message, '')
    else:
        item_text = ''' \n
        Item Id: {} \n
        Item content: {} \n
        '''.format(issue.item_id, issue.item.content)
        item_html = '''
        <h1 style="color: #ffcc00;">Item Id:</h1>
        <p>{}</p>
        <h1 style="color: #ffcc00;">Item content:</h1>
        <p>{}</p>'''.format(issue.item_id, issue.item.content)

        body_text = body_text.format(issue.category, issue.message, item_text)
        body_html = body_html.format(issue.category, issue.message, item_html)

    charset = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=aws_region)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    mail_adress,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=mail_adress,
        )
        logger.info("Notification email sent. SES Message ID: {}".format(
            response['MessageId']))
        return True
    except ClientError as e:
        logging.exception("Could not send mail notification. SNS Error: {}".format(
            e.response['Error']['Message']))
        return False
