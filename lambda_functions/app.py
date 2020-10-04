import logging
import json
import os
import boto3
import SearchFactChecks

from datetime import datetime
import requests

from crud import operations, helper, notifications
from crud.model import Item, User, Review, ReviewInProgress, ReviewAnswer, ReviewQuestion, User, Entity, Keyphrase, Sentiment, URL, ItemEntity, ItemKeyphrase, ItemSentiment, ItemURL, Base, Submission, FactChecking_Organization, ExternalFactCheck

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('stepfunctions')


def create_item(event, context, is_test=False, session=None):
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

    helper.log_method_initiated("Create item", event, logger)
    if session == None:
        session = operations.get_db_session(False, None)

    item = Item()
    body = event['body']
    helper.body_to_object(body, item)

    try:
        item = operations.create_item_db(item, is_test, session)
        return {
            "statusCode": 201,
            "body": json.dumps(item.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create item. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_items(event, context, is_test=False, session=None):
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
    if session == None:
        session = operations.get_db_session(False, None)

    helper.log_method_initiated("Get all items", event, logger)

    try:
        # Get all items as a list of Item objects
        items = operations.get_all_items_db(is_test, session)

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


def get_item_by_id(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get item by id", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['id']

        try:
            item = operations.get_item_by_id(id, is_test, session)

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


def get_factcheck_by_itemid(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get factchecks by item id", event, logger)

    if session is None:
        session = operations.get_db_session(is_test, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        try:
            factcheck = operations.get_factcheck_by_itemid_db(
                id, is_test, session)

            if factcheck is None:
                return {
                    "statusCode": 405,
                    "body": "Item or factcheck not found."
                }

            factcheck_dict = factcheck.to_dict()

            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(factcheck_dict)
            }
        except Exception:
            response = {
                "statusCode": 404,
                "body": "Item or factcheck not found."
            }

    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get factchecks. Check HTTP POST payload. Exception: {}".format(e)
        }
        
    response_cors = helper.set_cors(response, event, is_test)
    return response_cors


def get_online_factcheck_by_itemid(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get online factchecks by item id", event, logger)

    if session is None:
        session = operations.get_db_session(is_test, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        try:
            item = operations.get_item_by_id(id, is_test, session)
            entity_objects = operations.get_entities_by_itemid_db(id, is_test, session)
            phrase_objects = operations.get_phrases_by_itemid_db(id, is_test, session)
            title_entities = []  # entities from the claim title are stored as entities in the database

            entities = []
            for obj in entity_objects:
                entities.append(obj.to_dict()['entity'])
            phrases = []
            for obj in phrase_objects:
                phrases.append(obj.to_dict()['phrase'])

            event = {
                "item": item.to_dict(),
                "KeyPhrases": phrases,
                "Entities": entities,
                "TitleEntities": title_entities,
            }
            context = ""

            factcheck = SearchFactChecks.get_FactChecks(event, context)
            if 'claimReview' in factcheck[0]:
                factcheck_dict = {"id": "0", "url": factcheck[0]['claimReview'][0]['url'], "title": factcheck[0]['claimReview'][0]['title']}
                return {
                    "statusCode": 200,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body": json.dumps(factcheck_dict)
                }
            return {
                "statusCode": 404,
                "body": "No factcheck found."
            }

        except Exception:
            return {
                "statusCode": 404,
                "body": "No factcheck found."
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get item ID. Check HTTP POST payload. Exception: {}".format(e)
        }


def create_submission(event, context, is_test=False, session=None):

    helper.log_method_initiated("Create submission", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    body = event['body']
    submission = Submission()
    helper.body_to_object(body, submission)

    try:
        submission = operations.create_submission_db(
            submission, is_test, session)
        return {
            "statusCode": 201,
            "body": json.dumps(submission.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create submission. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_submissions(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get all submissions", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        submissions = operations.get_all_submissions_db(is_test, session)
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


def get_item_by_content(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get item by content", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        json_event = event['body']
        content = json_event.get('content')
        try:
            item = operations.get_item_by_content_db(content, is_test, session)
            item_serialized = {
                "id": item.id, "content": item.content, "language": item.language}
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


def create_user(event, context, is_test=False, session=None):

    helper.log_method_initiated("Create user", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        user = User()
        body = event['body']
        helper.body_to_object(body, user)

        # get cognito id
        id = str(event['requestContext']['identity']
                 ['cognitoAuthenticationProvider']).split("CognitoSignIn:", 1)[1]
        user.id = id

        user = operations.create_user_db(user, is_test, session)
        response = {
            "statusCode": 201,
            "body": json.dumps(user.to_dict())
        }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not create user. Check HTTP POST payload and Cognito authentication. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors


def create_user_from_cognito(event, context, is_test=False, session=None):

    helper.log_method_initiated("Create user from cognito", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    if event['triggerSource'] == "PostConfirmation_ConfirmSignUp":
        user = User()
        user.name = event['userName']
        user.id = event['request']['userAttributes']['sub']
        if user.id == None or user.name == None:
            raise Exception("Something went wrong!")
        user = operations.create_user_db(user, is_test, session)
        client = boto3.client('cognito-idp')
        client.admin_add_user_to_group(
            UserPoolId=event['userPoolId'],
            Username=user.name,
            GroupName='Detective'
        )

    return event


def get_all_users(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get all users", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        users = operations.get_all_users_db(is_test, session)
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


def get_user(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get user", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        # get cognito id
        id = helper.cognito_id_from_event(event)

        try:
            user = operations.get_user_by_id(id, is_test, session)
            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(user.to_dict())
            }
        except Exception:
            response = {
                "statusCode": 404,
                "body": "No user found with the specified id."
            }

    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get user. Check Cognito authentication. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors


def create_review(event, context, is_test=False, session=None):

    helper.log_method_initiated("Create review", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    review = Review()
    body = event['body']
    helper.body_to_object(body, review)

    try:
        review = operations.create_review_db(review, is_test, session)
        return {
            "statusCode": 201,
            "body": json.dumps(review.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create review. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_reviews(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get all reviews", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        reviews = operations.get_all_reviews_db(is_test, session)
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


def create_review_answer(event, context, is_test=False, session=None):

    helper.log_method_initiated("Create review answer", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    review_answer = ReviewAnswer()
    body = event['body']
    helper.body_to_object(body, review_answer)

    try:
        review_answer = operations.create_review_answer_db(
            review_answer, is_test, session)
        return {
            "statusCode": 201,
            "body": json.dumps(review_answer.to_dict())
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not create review answer. Check HTTP POST payload. Exception: {}".format(e)
        }


def get_all_review_answers(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get all review answers", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        review_answers = operations.get_all_review_answers_db(is_test, session)
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


def get_all_review_questions(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get all review questions", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        review_questions = operations.get_all_review_questions_db(
            is_test, session)
        review_questions_dict = []

        for review_question in review_questions:
            review_questions_dict.append(review_question.to_dict())

        response = {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(review_questions_dict)
        }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get review questions. Check HTTP GET payload. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors


def submit_review(event, context, is_test=False, session=None):

    helper.log_method_initiated("Submit review", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    # Parse Body of request payload into review object
    try:
        body = event['body']

        review = Review()
        helper.body_to_object(body, review)
        review.user_id = helper.cognito_id_from_event(event)

        if isinstance(body, str):
            body_dict = json.loads(body)
        else:
            body_dict = body

        review_answers = []

        for answer in body_dict['review_answers']:
            review_answer = ReviewAnswer()
            setattr(review_answer, "review_id", review.id)
            for key in answer:
                setattr(review_answer, key, answer[key])
            review_answers.append(review_answer)

        item = operations.review_submission_db(
            review, review_answers, is_test, session)

        operations.give_experience_point(review.user_id, is_test, session)

        if item.open_reviews_level_1 == 0 and item.open_reviews_level_2 == 0:
            item = operations.build_review_pairs(item, is_test, session)

        response = {
            "statusCode": 201,
            "body": json.dumps(item.to_dict())
        }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not submit review. Check HTTP GET payload. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors


def item_submission(event, context, is_test=False, session=None):

    helper.log_method_initiated("Item submission", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        body = event['body']

        if isinstance(body, str):
            body_dict = json.loads(body)
        else:
            body_dict = body
        content = body_dict["content"]
        del body_dict["content"]

        submission = Submission()
        helper.body_to_object(body_dict, submission)

        try:
            # Item already exists, item_id in submission is the id of the found item
            found_item = operations.get_item_by_content_db(
                content, is_test, session)
            submission.item_id = found_item.id
            new_item_created = False

        except Exception:
            # Item does not exist yet, item_id in submission is the id of the newly created item
            new_item = Item()
            new_item.open_timestamp = helper.get_date_time_now(is_test)
            new_item.content = content
            created_item = operations.create_item_db(
                new_item, is_test, session)
            new_item_created = True
            submission.item_id = created_item.id
            stage = os.environ['STAGE']
            client.start_execution(
                stateMachineArn='arn:aws:states:eu-central-1:891514678401:stateMachine:SearchFactChecks-'+stage,
                name='SFC_' + created_item.id,
                input="{\"item\":" + json.dumps(created_item.to_dict()) + "}"
            )

        # Create submission
        operations.create_submission_db(submission, is_test, session)

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


def get_open_items_for_user(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get open items for user", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        # get cognito user id
        id = helper.cognito_id_from_event(event)

        # get number of items from url path
        num_items = int(event['pathParameters']['num_items'])

        user = operations.get_user_by_id(id, is_test, session)
        items = operations.get_open_items_for_user_db(
            user, num_items, is_test, session)

        if len(items) < 1:
            response = {
                "statusCode": 404,
                "body": "There are currently no open items for this user."
            }
        else:
            # Transform each item into dict
            items_dict = []
            for item in items:
                items_dict.append(item.to_dict())

            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(items_dict)
            }

    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get user and/or num_items. Check URL path parameters. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors


def reset_locked_items(event, context, is_test=False, session=None):

    helper.log_method_initiated("Reset locked items", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        reviews_in_progress = operations.get_old_reviews_in_progress(
            is_test, session)
        operations.delete_old_reviews_in_progress(
            reviews_in_progress, is_test, session)
        return {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": "Items updated"
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Something went wrong. Check HTTP POST payload. Exception: {}".format(e)
        }


def accept_item(event, context, is_test=False, session=None):

    helper.log_method_initiated("Accept item", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        # get item id from url path
        item_id = event['pathParameters']['item_id']

        # get cognito id
        user_id = helper.cognito_id_from_event(event)

        # get user and item from the db
        user = operations.get_user_by_id(user_id, is_test, session)
        item = operations.get_item_by_id(item_id, is_test, session)

        # Try to accept item
        try:
            operations.accept_item_db(user, item, is_test, session)

            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(item.to_dict())
            }

        except Exception as e:
            response = {
                "statusCode": 400,
                "body": "Cannot accept item. Exception: {}".format(e)
            }

    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get user and/or item. Check URL path parameters. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors


def get_all_closed_items(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get all closed items", event, logger)

    if session == None:
        session = operations.get_db_session(False, None)

    try:
        # Get all closed items
        items = operations.get_all_closed_items_db(is_test, session)

        if len(items) == 0:
            response = {
                "statusCode": 404,
                "body": "No closed items found"
            }
        else:
            items_dict = []

            for item in items:
                items_dict.append(item.to_dict())

            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(items_dict)
            }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get closed items. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
