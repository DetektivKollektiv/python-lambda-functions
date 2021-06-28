import logging
import json
import traceback
from uuid import uuid4
from core_layer import helper
from core_layer import connection_handler
from core_layer.model.comment_model import Comment
from core_layer.handler import user_handler, review_handler, review_answer_handler
import notifications


def update_review(event, context, is_test=False, session=None):
    """Updates an existing review

    Args:
        event: AWS API Gateway event
        context ([type]): [description]
        is_test (bool, optional): Whether the function is executed in test mode. Defaults to False.
        session (optional): An sql alchemy session. Defaults to None.

    Returns
    ------
    - Status code 200, 400, 404 or 500 (Created)
    - The updated review
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Create Review", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        user_id = helper.cognito_id_from_event(event)
        body = json.loads(event['body']) if isinstance(
            event['body'], str) else event['body']

    except:
        return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event, is_test)

    if 'id' not in body:
        return helper.get_text_response(400, "Malformed request. Please provide a review id.", event, is_test)

    try:
        review = review_handler.get_review_by_id(
            body['id'], is_test, session)
    except:
        return helper.get_text_response(404, "No review found", event, is_test)

    # Save qualitative_comment
    if 'qualitative_comment' in body:
        try:
            comments_obj = Comment(id = str(uuid4()), 
                                   user_id = body['user_id'],
                                   comment = body['qualitative_comment'],
                                   item_id = body['item_id']
                                   )
            session.add(comments_obj)
            session.commit()
        except:
            return helper.get_text_response(404, "No qualitative comment found.", event, is_test)

    try:
        user = user_handler.get_user_by_id(user_id, is_test, session)
    except:
        return helper.get_text_response(404, "No user found.", event, is_test)

    if review.user_id != user.id:
        return helper.get_text_response(403, "Forbidden.", event, is_test)

    # If review is set closed
    if 'status' in body and body['status'] == 'closed':
        try:
            review = review_handler.close_review(review, is_test, session)
            if review.item.status == 'closed':
                notifications.notify_users(is_test, session, review.item)
            response = {
                "statusCode": 200,
                "body": json.dumps(review.to_dict_with_questions_and_answers())
            }
            response_cors = helper.set_cors(response, event, is_test)
            return response_cors
        except:
            return helper.get_text_response(500, "Internal server error. Stacktrace: {}".format(traceback.format_exc()), event, is_test)

    # If answers are appended
    elif 'questions' in body:
        if not isinstance(body['questions'], list):
            return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event, is_test)
        for question in body['questions']:
            if 'answer_value' in question:
                answer_value = question['answer_value']
            else:
                return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event, is_test)

            if answer_value is not None:
                # Check if conditionality is met
                if question['parent_question_id'] is not None:
                    for q in body['questions']:
                        if q['question_id'] == question['parent_question_id']:
                            parent_question = q
                    parent_answer = review_answer_handler.get_parent_answer(
                        question['answer_id'], is_test, session)
                    if parent_question['answer_value'] > question['upper_bound'] or parent_question['answer_value'] < question['lower_bound']:
                        return helper.get_text_response(400, "Bad request. Please adhere to conditionality of questions.", event, is_test)
                # Update answer in db
                try:
                    review_answer_handler.set_answer_value(
                        question['answer_id'], question['answer_value'], is_test, session)
                except:
                    return helper.get_text_response(500, "Internal server error. Stacktrace: {}".format(traceback.format_exc()), event, is_test)

        response = {
            "statusCode": 200,
            "body": json.dumps(review.to_dict_with_questions_and_answers())
        }
        response_cors = helper.set_cors(response, event, is_test)
        return response_cors

    else:
        return helper.get_text_response(400, "Bad request. Please adhere to conditionality of questions.", event, is_test)