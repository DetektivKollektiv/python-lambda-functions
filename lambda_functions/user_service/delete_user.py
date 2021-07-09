import logging
import traceback
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import user_handler


def delete_user(event, context):
    """Deletes a user from DB and Cognito.

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
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Delete user", event, logger)

    with Session() as session:
        try:
            user_handler.delete_user(event, session)

            response = {
                "statusCode": 200
            }

        except Exception:
            response = {
                "statusCode": 500,
                "body": "User could not be deleted. Exception: {}".format(traceback.format_exc())
            }

        response_cors = helper.set_cors(response, event)
        return response_cors
