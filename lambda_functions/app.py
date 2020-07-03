import logging
import json

from aws_xray_sdk.core import patch_all
from aws_xray_sdk.core import xray_recorder

from crud import operations
from crud.model import Item, Submission


def create_item(event, context):
    """Creates a new item.

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    
    print(event)
    
    # Parse event dict (= http post payload) to Item object
    item = Item()
    json_event = event['body']
    for key in json_event:
        setattr(item, key, json_event[key])

    try:
        item = operations.create_item_db(item)
        return {
            "statusCode": 201,
            "body": json.dumps(item.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create item. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_items(event, context):
    """Gets all items.

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # X-Ray Tracing
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # patch_all()

    logger.info('Database access for item retrieval.')


    try:
        # New x-ray segment
        xray_recorder.begin_subsegment('database-access')

        # Get all items as a list of Item objects
        items = operations.get_all_items_db()

        xray_recorder.end_subsegment()

        items_dict = []
        for item in items:
            items_dict.append(item.to_dict())

        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(items_dict)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get items. Check HTTP GET payload. Exception: {}".format(e)
        }


def create_submission(event, context):

    submission = Submission()

    json_event = event['body']
    for key in json_event:
        setattr(submission, key, json_event[key])

    try:
        submission = operations.create_submission_db(submission)
        return {
            "statusCode": 201,
            "body": json.dumps(submission.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create submission. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_submissions(event, context):

    try:
        submissions = operations.get_all_submissions_db()
        submissions_dict = []

        for submission in submissions:
            submissions_dict.append(submission.to_dict())

        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(submissions_dict)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get submissions. Check HTTP GET payload. Exception: {}".format(e)
        }


def get_item_by_content(event, context):

    try:
        json_event = event['body']
        content = json_event.get('content')
        try:
            item = operations.get_item_by_content_db(content)
            item_serialized = {"id": item.id, "content": item.content, "language": item.language}
            return {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(item_serialized)
            }
        except Exception:
            return {
                "statusCode": 404,
                "body": "No item found with the specified content."
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get item. Check HTTP GET payload. Exception: {}".format(e)
        }