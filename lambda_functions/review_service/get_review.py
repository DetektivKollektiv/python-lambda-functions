import logging
import json
import traceback
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import user_handler, review_handler


def get_review(event, context):
    """Gets a review.

    Parameters
    ----------
    - user_id is retrieved from the event
    - review_id is retrieved from query parameters

    Returns
    ------
    - Status code 200 OK
    - The requested review
    """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Get Review", event, logger)
    
    try:
        # get review id from url query params
        review_id = event['pathParameters']['review_id']
        # get cognito id
        user_id = helper.cognito_id_from_event(event)
    except:
        return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event)        

    with Session() as session:

        try:
            # get user from database
            user = user_handler.get_user_by_id(user_id, session)
        except:
            return helper.get_text_response(404, "No user found.", event)
            
        try:
            # Try to receive review
            review = review_handler.get_review_by_id(review_id, session)
        except:
            return helper.get_text_response(404, "No review found", event)

        try:
            if review.user_id == user.id:
                response = {
                    "statusCode": 200,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body": json.dumps(review.to_dict_with_questions_and_answers())
                }
            else:
                return helper.get_text_response(403, "Forbidden", event)

        except:
            return helper.get_text_response(500, "Internal server error. Stacktrace: {}".format(traceback.format_exc()), event)

        response_cors = helper.set_cors(response, event)
        return response_cors
