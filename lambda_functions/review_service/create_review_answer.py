# External imports
import logging
import json
import traceback
from uuid import uuid4
# Helper imports
from core_layer import helper
from core_layer.connection_handler import get_db_session, update_object
# Model imports
from core_layer.model.review_answer_model import ReviewAnswer
# Handler imports
from core_layer.handler import review_answer_handler, review_handler, review_pair_handler, item_handler, user_handler
import notifications


def create_review_answer(event, context, is_test=False, session=None):
    """Creates a new review answer

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        #api-gateway-simple-proxy-for-lambda-input-format
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        helper.log_method_initiated("Get item by id", event, logger)

        if session == None:
            session = get_db_session(is_test, session)

        # Create actual review answer object
        review_answer = ReviewAnswer()
        helper.body_to_object(event['body'], review_answer)
        review_answer_handler.create_review_answer(
            review_answer, is_test, session)

        # Get partner review
        review = review_handler.get_review_by_id(
            review_answer.review_id, is_test, session)
        pair = review_pair_handler.get_review_pair_from_review(
            review, is_test, session)
        partner_review = review_handler.get_partner_review(
            review, is_test, session)

        # Check if review is closed (i.e. 7 questions were answered)
        if(len(review.review_answers) == 7):

            review.status = "closed"
            user_handler.give_experience_point(
                review.user_id, is_test, session)

            if(partner_review != None):
                # Check if partner review is complete
                if len(partner_review.review_answers) == 7:
                    # Check if answers cause review to be bad (e.g. answer is 0 but partner answer is any other value)
                    pair.is_good = True
                    for answer in review.review_answers:
                        partner_answer = review_answer_handler.get_partner_answer(
                            partner_review, answer.review_question_id, is_test, session)
                        if partner_answer == None:
                            pair.is_good = False
                        else:
                            if((review_answer.answer == 0 and partner_answer.answer != 0) or (review_answer.answer != 0 and partner_answer.answer == 0)):
                                pair.is_good = False

                    if (pair.is_good):
                        variance = review_pair_handler.compute_variance(pair)
                        pair.variance = variance
                        if(variance <= 1):
                            pair.is_good = True
                        else:
                            pair.is_good = False

                    review.item.in_progress_reviews_level_1 -= 1
                    review.item.in_progress_reviews_level_2 -= 1
                    if pair.is_good:
                        review.item.open_reviews -= 1
                        review.item.open_reviews_level_1 -= 1
                        review.item.open_reviews_level_2 -= 1

        # Check if item is closed (i.e. four "good" pairs)
        pairs = review_pair_handler.get_review_pairs_by_item(
            pair.item_id, is_test, session)

        if(len(list(filter(lambda p: p.is_good, pairs))) >= 4):
            review.item.status = "closed"
            review.item.result_score = item_handler.compute_item_result_score(
                review.item_id, is_test, session)

            # Notify email and telegram users
            notifications.notify_users(is_test, session, review.item)

        update_object(review, is_test, session)
        update_object(pair, is_test, session)
        update_object(review.item, is_test, session)

        response = {
            "statusCode": 201,
            "body": json.dumps(review_answer.to_dict())
        }

    except Exception:
        response = {
            "statusCode": 500,
            "body": "Review answer could not be created. Exception: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
