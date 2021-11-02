import logging
import json
import traceback
from core_layer import helper, responses
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
            review = review_handler.get_open_review(user_id, session)
        except:
            return helper.get_text_response(404, "No review found", event)
        if review is None:
            return responses.NoContent(event, 'No review in progress found for current user.').to_json_string()
        try:
            if review.user_id == user.id:
                return responses.Success(event, json.dumps(review.to_dict(with_questions_and_answers=True, with_tags=True))).to_json_string()
            else:
                return responses.Forbidden(event, 'User is not allowed to access review').to_json_string()
        except Exception as e:
            return responses.InternalError(event, "Internal error", e).to_json_string()
