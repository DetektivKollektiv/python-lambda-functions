import logging
import json

from aws_xray_sdk.core import patch_all
from aws_xray_sdk.core import xray_recorder

from crud import operations
from crud.model import *


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

    item = Item()
    body = event['body']
    operations.body_to_object(body, item)

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


def get_item_by_id(event, context):

    try:
        # get id (str) from path
        id = event['pathParameters']['id']

        try:
            item = operations.get_item_by_id(id)
            return {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(item.to_dict())
            }
        except Exception:
            return {
                "statusCode": 404,
                "body": "No item found with the specified id."
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get item. Check HTTP POST payload. Exception: {}".format(e)
        }


def create_submission(event, context):

    body = event['body']
    submission = Submission()
    operations.body_to_object(body, submission)

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


def create_user(event, context):

    user = User()
    body = event['body']
    operations.body_to_object(body, user)

    try:
        user = operations.create_user_db(user)
        return {
            "statusCode": 201,
            "body": json.dumps(user.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create user. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_users(event, context):

    try:
        users = operations.get_all_users_db()
        users_dict = []

        for user in users:
            users_dict.append(user.to_dict())

        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(users_dict)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get users. Check HTTP GET payload. Exception: {}".format(e)
        }


def get_user_by_id(event, context):

    try:
        # get id (str) from path
        id = event['pathParameters']['id']

        try:
            user = operations.get_user_by_id(id)
            return {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(user.to_dict())
            }
        except Exception:
            return {
                "statusCode": 404,
                "body": "No user found with the specified id."
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get user. Check HTTP POST payload. Exception: {}".format(e)
        }


def create_review(event, context):

    review = Review()
    body = event['body']
    operations.body_to_object(body, review)

    try:
        review = operations.create_review_db(review)
        return {
            "statusCode": 201,
            "body": json.dumps(review.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create review. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_reviews(event, context):

    try:
        reviews = operations.get_all_reviews_db()
        reviews_dict = []

        for review in reviews:
            reviews_dict.append(review.to_dict())

        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(reviews_dict)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get reviews. Check HTTP GET payload. Exception: {}".format(e)
        }


def create_review_answer(event, context):

    review_answer = ReviewAnswer()
    body = event['body']
    operations.body_to_object(body, review_answer)

    try:
        review_answer = operations.create_review_answer_db(review_answer)
        return {
            "statusCode": 201,
            "body": json.dumps(review_answer.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create review answer. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_review_answers(event, context):

    try:
        review_answers = operations.get_all_review_answers_db()
        review_answers_dict = []

        for review_answer in review_answers:
            review_answers_dict.append(review_answer.to_dict())

        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(review_answers_dict)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get review answers. Check HTTP GET payload. Exception: {}".format(e)
        }


def get_all_review_questions(event, context):

    try:
        review_questions = operations.get_all_review_questions_db()
        review_questions_dict = []

        for review_question in review_questions:
            review_questions_dict.append(review_question.to_dict())

        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(review_questions_dict)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get review questions. Check HTTP GET payload. Exception: {}".format(e)
        }


def item_submission(event, context):

    try:
        body = event['body']

        if isinstance(body, str): 
            body_dict = json.loads(body)
        else: 
            body_dict = body

        content = body_dict["content"]
        del body_dict["content"]

        submission = Submission()
        operations.body_to_object(body_dict, submission)

        try:
            # Item already exists, item_id in submission is the id of the found item
            found_item = operations.get_item_by_content_db(content)
            submission.item_id = found_item.id
            new_item_created = False
            
        except Exception:
            # Item does not exist yet, item_id in submission is the id of the newly created item
            new_item = Item()
            new_item.content = content
            created_item = operations.create_item_db(new_item)
            new_item_created = True
            submission.item_id = created_item.id

        # Create submission
        operations.create_submission_db(submission)

        return {
            "statusCode": 201,
            'headers': {"content-type": "application/json; charset=utf-8", "new-item-created": str(new_item_created), "Access-Control-Allow-Origin": "*" },
            "body": json.dumps(submission.to_dict())
        }
       
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create item and/or submission. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_open_item_for_user(event, context):

    try:
        # get user id (str) from path
        id = event['pathParameters']['id']

        try:
            user = operations.get_user_by_id(id)
            item = operations.get_open_item_for_user_db(user)

            return {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(item.to_dict())
            }
        except Exception:
            return {
                "statusCode": 404,
                "body": "No open item found for the specified user."
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get user. Check HTTP POST payload. Exception: {}".format(e)
        }
