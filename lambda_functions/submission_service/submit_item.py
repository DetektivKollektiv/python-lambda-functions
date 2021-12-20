import logging
import json
import re
import os
import io
import traceback
import unicodedata
import boto3
from botocore.exceptions import ClientError

from core_layer import helper
from core_layer.db_handler import Session
from core_layer.model.item_model import Item
from core_layer.model.submission_model import Submission
from core_layer.handler import item_handler, submission_handler, url_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def remove_control_characters(s):
    s_clean = s.replace("\"", " ")
    return "".join(ch for ch in s_clean if unicodedata.category(ch)[0] != "C")


def submit_item(event, context):
    client = boto3.client('stepfunctions', region_name="eu-central-1")

    helper.log_method_initiated("Item submission", event, logger)

    with Session() as session:

        try:
            body = event['body']

            if isinstance(body, str):
                body_dict = json.loads(body)
            else:
                body_dict = body
            content = body_dict["content"]
            del body_dict["content"]

            if "type" in body_dict:
                type = body_dict["type"]
                del body_dict["type"]
            else:
                type = None

            if "item_type_id" in body_dict:
                item_type_id = body_dict["item_type_id"]
                del body_dict["item_type_id"]
            else:
                item_type_id = None

            if "item" in body_dict:
                del body_dict["item"]

            submission = Submission()
            helper.body_to_object(body_dict, submission)
            # add ip address
            ip_address = event['requestContext']['identity']['sourceIp']
            setattr(submission, 'ip_address', ip_address)

            try:
                # Item already exists, item_id in submission is the id of the found item                
                item = item_handler.get_item_by_content(content, session)
                submission.item_id = item.id
                new_item_created = False

            except Exception:
                # Item does not exist yet, item_id in submission is the id of the newly created item
                item = Item()
                item.content = content
                item.item_type_id = item_type_id
                item.type = type
                item = item_handler.create_item(item, session)
                new_item_created = True

                if content:
                    str_urls = re.findall('http[s]?://(?:[a-zA-ZäöüÄÖÜ]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
                    url_handler.prepare_and_store_urls(item, str_urls, session)

                submission.item_id = item.id
                submission.status = item.status

            # Create submission
            submission_handler.create_submission_db(submission, session)
            if submission.mail:
                if item.status != 'Unsafe':
                    send_confirmation_mail(submission)

            # Create response
            if item.status == 'Unsafe':
                response = {
                    "statusCode": 403,
                    "headers": {"content-type": "application/json; charset=utf-8", "new-item-created": str(new_item_created)},
                    "body": "Item not valid"
                }
            else:
                response = {
                    "statusCode": 201,
                    "headers": {"content-type": "application/json; charset=utf-8", "new-item-created": str(new_item_created)},
                    "body": json.dumps(item.to_dict())
                }

        except Exception as e:
            logger.error("Couldn't submit item. Exception: %s", e)
            response = {
                "statusCode": 400,
                "body": "Could not create item and/or submission. Check HTTP POST payload. Stacktrace: {}".format(traceback.format_exc())
            }

    ## start SearchFactChecks only for safe items
    if (item.status != 'Unsafe') and (new_item_created == True):
        stage = os.environ['STAGE']
        client.start_execution(
            stateMachineArn='arn:aws:states:eu-central-1:891514678401:stateMachine:SearchFactChecks_new-' + stage,
            name='SFC_' + item.id,
            input="{\"item\":{"
                    "\"id\":\"" + item.id + "\","
                                          "\"content\":\"" + remove_control_characters(item.content) + "\" } }"
        )

    response_cors = helper.set_cors(response, event)
    return response_cors


def send_confirmation_mail(submission: Submission):
    stage = os.environ['STAGE']
    if stage == 'prod':
        confirmation_link = 'https://api.codetekt.org/submission_service/submissions/{}/confirm'.format(
            submission.id)
    else:
        confirmation_link = 'https://api.{}.codetekt.org/submission_service/submissions/{}/confirm'.format(
            stage, submission.id)

    if submission.mail:
        recipient = submission.mail
    else:
        return
    sender = "codetekt <no-reply@codetekt.org>"
    subject = 'Bestätige deine Mail-Adresse'

    body_text = "Bitte bestätige deine Mailadresse durch Klick auf folgenden Link {}".format(confirmation_link)
    body_html = io.open(os.path.join(os.path.dirname(__file__), 'resources',
                                     'confirmation_file_body.html'), mode='r', encoding='utf-8').read().format(confirmation_link)

    charset = "UTF-8"
    client = boto3.client('ses', region_name='eu-central-1')
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
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
            Source=sender,
        )
        logger.info("Confirmation email sent for submission with ID: {}. SES Message ID: {}".format(
            submission.id, response['MessageId']))

    except ClientError as e:
        logging.exception("Could not send confirmation mail for submission with ID: {}. SNS Error: {}".format(
            submission.id, e.response['Error']['Message']))
        pass
