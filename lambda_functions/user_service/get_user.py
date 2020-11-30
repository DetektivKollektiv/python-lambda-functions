import logging
import json
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import user_handler


def get_user(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get user", event, logger)

    if session == None:
        session = get_db_session(False, None)

    try:
        # get cognito id
        id = helper.cognito_id_from_event(event)

        try:
            user = user_handler.get_user_by_id(id, is_test, session)
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
