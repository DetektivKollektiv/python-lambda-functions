import logging
import json
import traceback
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import user_handler

def get_top_users(event, context, is_test=False, session=None):
    # todo, change to a query param,  with max 100 ??(i suppose)
    n = 10

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get Top n Users", event, logger)

    if session == None:
        session = get_db_session(False, None)

    #todo: can we get rid of the try{}except{} here? 
    try:
        descending = True
        attr = 'experience_points'
        users = user_handler.get_top_users(n, attr, descending, is_test, session)
        response = {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps([user.to_dict() for user in users])
        }
    except Exception:
        response = {
            "statusCode": 500,
            "body": "Server Error. Stacktrace: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
