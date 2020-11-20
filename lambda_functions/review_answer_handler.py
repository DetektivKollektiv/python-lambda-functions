import logging
from uuid import uuid4
from crud import operations, helper, notifications
from crud.model import ReviewAnswer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def create_review_answer(event, context, is_test=False, session=None):
    """Creates a new review answer

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
        helper.log_method_initiated("Get item by id", event, logger)

        if session == None:
            session = operations.get_db_session(is_test, session)
        
        # Create actual review answer object
        review_answer = ReviewAnswer()
        helper.body_to_object(event['body'], review_answer)
        operations.create_review_answer_db(review_answer, is_test, session)

        # Get partner review
        review = operations.get_review_by_id(review_answer.review_id, is_test, session)
        pair = operations.get_review_pair(review.review_id, is_test, session)
        partner_review = operations.get_partner_review(review, is_test, session)

        # Check if answer cause review to be bad (e.g. answer is 0 but partner answer is any other value)
        if(partner_review != None):
            partner_answer = operations.get_partner_answer(partner_review, review_answer.review_question_id, is_test, session)
            
            if(partner_answer == None):
                pair.is_good = False
            else:
                if((review_answer.answer == 0 and partner_answer.answer != 0) or (review_answer.answer != 0 and partner_answer.answer == 0)):
                    pair.is_good = False

        # Check if review is closed (i.e. 7 questions were answered)
        if(len(review.review_answers) == 7):
            review.status = "closed"
            operations.update_object_db(review, is_test, session)
            if(partner_review != None):
                if(pair.is_good):
                    variance = operations.compute_variance(pair)
                    pair.variance = variance
                    if(variance <= 1):
                        pair.is_good = True
                    else:
                        pair.is_good = False
            operations.update_object_db(pair, is_test, session)

        # Check if item is closed (i.e. four "good" pairs)
        pairs = operations.get_review_pairs_by_item(pair.item_id, is_test, session)

        if(len(list(filter(lambda p: p.is_good, pairs))) >= 4):
            review.item.status = "closed"
            review.item.result_score = operations.compute_item_result_score(review.item_id, is_test, session)
            operations.update_object_db(review.item, is_test, session)

            # Notify email and telegram users
            notifications.notify_users(is_test, session, review.item)

        response = {
            "statusCode": 200,
            "body": review_answer
        }

    except Exception as exception:
        response = {
            "statusCode": 500,
            "body": "Review answer could not be created. Exception: {}".format(exception)
        }
    
    response_cors = helper.set_cors(response, event, is_test)
    return response_cors