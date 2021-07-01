import logging
import json
import traceback

from core_layer.db_handler import Session
from core_layer.handler import user_handler
from core_layer import helper


def get_user_ranking(event, context):
    """
    returns a dictionary with
    list top_users:           10 top users
    list top_users_by_level:  10 top users on the user's level 
    list top_users_by_period: 10 top users in a period p (1 week)
    """
    n = 10
    p = 1
    
    descending = True
    attr = 'experience_points'
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get User Ranking", event, logger)

    user_ranking_dict = {}

    top_users_list = []
    top_users_by_level_list = []
    top_users_by_period_list = []

    try:        
        my_user_id = helper.cognito_id_from_event(event)
    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not get User. Check Cognito Authentication. Stacktrace: {}".format(traceback.format_exc())
        }

    with Session() as session:

        try:
            helper.log_method_initiated("Get Top n Users", event, logger) 
            top_users = user_handler.get_top_users(n, attr, descending, session)
            for user in top_users:            
                top_users_list.append(user.to_dict())
            user_ranking_dict['top_users'] = top_users_list    

            helper.log_method_initiated("Get Top n Users on the User's Level", event, logger)
            my_user = user_handler.get_user_by_id(my_user_id, session)
            user_level = my_user.level_id
            top_users_by_level = user_handler.get_top_users_by_level(user_level, n, attr, descending, session)
            for user in top_users_by_level:            
                top_users_by_level_list.append(user.to_dict())
            user_ranking_dict['top_users_by_level'] = top_users_by_level_list
            
            helper.log_method_initiated("Get Top n Users in a Period", event, logger)   
            top_users_by_period = user_handler.get_top_users_by_period(n, p, attr, descending, session)
            for user in top_users_by_period:            
                top_users_by_period_list.append(user.to_dict())
            user_ranking_dict['top_users_by_period'] = top_users_by_period_list
            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(user_ranking_dict)
            }

        except Exception:
            response = {
                "statusCode": 500,
                "body": "Server Error. Stacktrace: {}".format(traceback.format_exc())
            }     
   
    response_cors = helper.set_cors(response, event)
    return response_cors
