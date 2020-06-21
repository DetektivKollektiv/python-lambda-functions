import json

from crud.model import Item, Submission
from crud import operations


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

    # Parse event dict (= http post payload) to Item object
    item = Item()
    for key in event:
        setattr(item, key, event[key])

    try:
        operations.create_item_db(item)
        return {
            "statusCode": 201,
            "body": "Item created successfully."
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

    try:
        # Get all items as a list of Item objects
        items = operations.get_all_items_db()

        # Prepare response payload (list of serialized items)
        # TODO automatically serialize / dump objects (json.dumps cannot serialize custom classes like Item)
        items_serialized = []
        for item in items:
            items_serialized.append({"content": item.content, "language": item.language})

        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": items_serialized
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get items. Check HTTP GET payload. Exception: {}".format(e)
        }

def create_submission(event, context):

    submission = Submission()

    json_event = json.loads(event['body'])
    for key in json_event:
        setattr(submission, key, json_event[key])

    try:
        operations.create_submission_db(submission)
        return {
            "statusCode": 201,
            "body":"Submission created successfully"
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create submission. Check HTTP POST payload. Exception: {}".format(e)
        }

def get_all_submissions(event, context):

    try:
        submissions = operations.get_all_submissions_db()
        submissions_serialized = []

        for submission in submissions:
            submissions_serialized.append({"item_id": submission.item_id, "submission_date":submission.submission_date,
                                           "received_date":submission.received_date, "phone":submission.phone, "mail":submission.mail,
                                           "source":submission.source, "frequency":submission.frequency})
        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(submissions_serialized)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get submissions. Check HTTP GET payload. Exception: {}".format(e)
        }