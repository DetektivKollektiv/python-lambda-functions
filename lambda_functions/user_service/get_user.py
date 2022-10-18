import logging
import json
import traceback
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import user_handler, mail_handler


def get_user(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get user", event, logger)

    with Session() as session:

        try:
            # get cognito id
            id = helper.cognito_id_from_event(event)

            try:
                user = user_handler.get_user_by_id(id, session)
                user_dict = user.to_dict()
                progress = user_handler.get_user_progress(user, session)
                total_rank = user_handler.get_user_rank(user, False, session)
                level_rank = user_handler.get_user_rank(user, True, session)
                solved_cases_total = user_handler.get_solved_cases(
                    user, False, session)
                solved_cases_today = user_handler.get_solved_cases(
                    user, True, session)
                exp_needed = user_handler.get_needed_exp(user, session)
                try:
                    mail = mail_handler.get_mail_by_user_id(id, session)
                    user_dict['mail_status'] = mail.status
                except:
                    user_dict['mail_status'] = 'none'
                user_dict['progress'] = progress
                user_dict['total_rank'] = total_rank
                user_dict['level_rank'] = level_rank
                user_dict['solved_cases_total'] = solved_cases_total
                user_dict['solved_cases_today'] = solved_cases_today
                user_dict['exp_needed'] = exp_needed
                user_dict['closed_items'] = [
                    review.item.to_dict(with_tags=True) for review in user.reviews if review.item.status == "closed"]
                response = {
                    "statusCode": 200,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body": json.dumps(user_dict)
                }
            except Exception:
                response = {
                    "statusCode": 404,
                    "body": "No user found with the specified id.{}".format(traceback.format_exc())
                }

        except Exception:
            response = {
                "statusCode": 400,
                "body": "Could not get user. Check Cognito authentication. Stacktrace: {}".format(traceback.format_exc())
            }

    response_cors = helper.set_cors(response, event)
    return response_cors
