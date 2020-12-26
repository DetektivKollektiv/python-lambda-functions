import logging
import json
import boto3
import os

from core_layer import helper, connection_handler
from core_layer.model.item_model import Item
from core_layer.model.submission_model import Submission
from core_layer.handler import item_handler, submission_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def submit_item(event, context, is_test=False, session=None):

    client = boto3.client('stepfunctions')

    helper.log_method_initiated("Item submission", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        body = event['body']

        if isinstance(body, str):
            body_dict = json.loads(body)
        else:
            body_dict = body
        content = body_dict["content"]
        del body_dict["content"]
        type = body_dict["type"]
        del body_dict["type"]

        submission = Submission()
        helper.body_to_object(body_dict, submission)

        try:
            # Item already exists, item_id in submission is the id of the found item
            found_item = item_handler.get_item_by_content(
                content, is_test, session)
            submission.item_id = found_item.id
            new_item_created = False

        except Exception:
            # Item does not exist yet, item_id in submission is the id of the newly created item
            new_item = Item()
            new_item.content = content
            new_item.type = type
            created_item = item_handler.create_item(
                new_item, is_test, session)
            new_item_created = True
            submission.item_id = created_item.id
            stage = os.environ['STAGE']
            client.start_execution(
                stateMachineArn='arn:aws:states:eu-central-1:891514678401:stateMachine:SearchFactChecks_new-'+stage,
                name='SFC_' + created_item.id,
                input="{\"item\":{" \
                            "\"id\":\"" + created_item.id + "\"," \
                            "\"content\":\"" + created_item.content + "\" } }"
            )

        # Create submission
        submission_handler.create_submission_db(submission, is_test, session)

        response = {
            "statusCode": 201,
            'headers': {"content-type": "application/json; charset=utf-8", "new-item-created": str(new_item_created)},
            "body": json.dumps(submission.to_dict())
        }

    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not create item and/or submission. Check HTTP POST payload. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
