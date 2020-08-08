import logging
import json
import os
import boto3
from datetime import datetime

from aws_xray_sdk.core import patch_all
from aws_xray_sdk.core import xray_recorder

from crud import operations
from crud.model import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

    try:
        user = User()
        body = event['body']
        operations.body_to_object(body, user)

        # get cognito id
        id = str(event['requestContext']['identity']['cognitoAuthenticationProvider']).split("CognitoSignIn:",1)[1] 
        user.id = id

        user = operations.create_user_db(user)
        response = {
            "statusCode": 201,
            "body": json.dumps(user.to_dict())
        }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not create user. Check HTTP POST payload and Cognito authentication. Exception: {}".format(e)
        }
    
    response_cors = operations.set_cors(response, event)
    return response_cors

def create_user_from_cognito(event, context):
    
    if event['triggerSource'] == "PostConfirmation_ConfirmSignUp":
        user = User()
        user.name = event['userName']
        user.id = event['request']['userAttributes']['sub']
        if user.id == None or user.name == None:
            raise Exception("Something went wrong!")
        user = operations.create_user_db(user)
        client = boto3.client('cognito-idp')
        client.admin_add_user_to_group(
            UserPoolId = event['userPoolId'],
            Username = user.name,
            GroupName ='Detective'
        )

    return event

    
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


def get_user(event, context):

    try:
        # get cognito id
        id = str(event['requestContext']['identity']['cognitoAuthenticationProvider']).split("CognitoSignIn:",1)[1] 

        try:
            user = operations.get_user_by_id(id)
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

    response_cors = operations.set_cors(response, event)
    return response_cors


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

        response = {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(review_questions_dict)
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Could not get review questions. Check HTTP GET payload. Exception: {}".format(e)
        }

    if 'headers' in event and 'Origin' in event['headers']:
        sourceOrigin = event['headers']['Origin']
    elif 'headers' in event and 'origin' in event['headers']:
        sourceOrigin = event['headers']['origin']
    else:
        return response

    allowedOrigins = os.environ['CORS_ALLOW_ORIGIN'].split(',') or []

    if sourceOrigin is not None and sourceOrigin in allowedOrigins:
        if 'headers' not in response:
            response['headers'] = {}
        
        response['headers']['Access-Control-Allow-Origin'] = sourceOrigin
    
    return response


def submit_review(event, context):
    
    #Parse Body of request payload into review object
    try:
        body = event['body']

        review = Review()
        review.user_id = operations.cognito_id_from_event(event)
        
        operations.body_to_object(body, review)
        
        #Give the user an experience point
        operations.give_experience_point(review.user_id)
        
        #Check if the review is still needed
        review_still_needed = operations.check_if_review_still_needed(review.item_id, review.user_id, review.is_peer_review)
        #If the review is no longer needed, return an error
        if review_still_needed == False:
            return {
                "statusCode": 400,
                "body": "Could not create review. Review no longer needed. Another detective might have been faster."
            }
        #If the review is needed, create the review and the answers

        #Get the corresponding item to know when it was locked by the user
        item = operations.get_item_by_id(review.item_id)

        # Set the review open and close timestamp
        if item.lock_timestamp:
            review.start_timestamp = item.lock_timestamp
            review.finish_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            review = operations.create_review_db(review)
        else:
            return {
                "statusCode": 400,
                "body": "Could not create review. To review an item, it has to be locked by the user."
            }

        # Deserialize if body is string 
        if isinstance(body, str): 
            body_dict = json.loads(body)
        else: 
            body_dict = body

        review_answers = []
        
        for answer in body_dict['review_answers']:
            review_answer = ReviewAnswer()
            setattr(review_answer, "review_id",review.id)
            for key in answer:
                setattr(review_answer, key, answer[key])
            review_answers.append(review_answer)

        operations.create_review_answer_set_db(review_answers)

        #If the review is a peer review, compute the variance of the review pair
        if review.is_peer_review == True:
            operations.close_open_junior_review(review.item_id, review.id)
            difference = operations.get_pair_difference(review.id)
            #If the variance is good, reduce the counter for open review pairs
            if difference < 1:
                operations.set_belongs_to_good_pair_db(review, True)
                item.open_reviews = item.open_reviews - 1
                #If enough review pairs have been found, set the status to closed
                if item.open_reviews == 0:
                    item.status = "closed"
                    item.close_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.result_score = operations.compute_item_result_score(item.id)
                else:
                    item.status = "needs_junior"
            if difference >= 1:
                operations.set_belongs_to_good_pair_db(review, False)
                item.status = "needs_junior"

        #If the review is not a peer review, set the status to "needs_senior"
        if review.is_peer_review == False:
            item.status = "needs_senior" 

        # Unlock item
        item.lock_timestamp = None
        item.locked_by_user = None

        operations.update_object_db(item)
        #for answer in review.review_answers
        #    operations.create_review_answer_db(answer)

        response = {
                "statusCode": 201,
                "body": json.dumps(item.to_dict())
            }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not submit review. Check HTTP GET payload. Exception: {}".format(e)
        }
    
    response_cors = operations.set_cors(response, event)
    return response_cors


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
            new_item.open_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_item.content = content
            created_item = operations.create_item_db(new_item)
            new_item_created = True
            submission.item_id = created_item.id

        # Create submission
        operations.create_submission_db(submission)

        response = {
            "statusCode": 201,
            'headers': {"content-type": "application/json; charset=utf-8", "new-item-created": str(new_item_created) },
            "body": json.dumps(submission.to_dict())
        }
       
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not create item and/or submission. Check HTTP POST payload. Exception: {}".format(e)
        }
        
    response_cors = operations.set_cors(response, event)
    return response_cors


def get_open_items_for_user(event, context):

    try:
        # get cognito user id
        id = operations.cognito_id_from_event(event)

        # get number of items from url path
        num_items = int(event['pathParameters']['num_items'])

        user = operations.get_user_by_id(id)
        items = operations.get_open_items_for_user_db(user, num_items)

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

    response_cors = operations.set_cors(response, event)
    return response_cors


def reset_locked_items(event, context):
    try:
        items = operations.get_locked_items()
        updated = operations.reset_locked_items_db(items)        
        return {
                    "statusCode": 200,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body":"{} Items updated".format(updated)
                }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Something went wrong. Check HTTP POST payload. Exception: {}".format(e)
        }


def accept_item(event, context):

    try:
        # get item id from url path
        item_id = event['pathParameters']['item_id']

        # get cognito id 
        user_id = str(event['requestContext']['identity']['cognitoAuthenticationProvider']).split("CognitoSignIn:",1)[1] 

        # get user and item from the db
        user = operations.get_user_by_id(user_id)
        item = operations.get_item_by_id(item_id)
            
        # Try to accept item
        try:
            operations.accept_item_db(user, item)

            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8" },
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
        
    response_cors = operations.set_cors(response, event)
    return response_cors


def get_all_closed_items(event, context):

    try:
        # Get all closed items
        items = operations.get_all_closed_items_db()

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

    response_cors = operations.set_cors(response, event)
    return response_cors
