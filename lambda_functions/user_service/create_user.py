import boto3
import logging

from core_layer import helper
from core_layer.connection_handler import get_db_session

from core_layer.model.user_model import User

from core_layer.handler import user_handler


def create_user(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Create user from cognito", event, logger)

    if session == None:
        session = get_db_session(False, None)

    if event['triggerSource'] == "PostConfirmation_ConfirmSignUp":
        user = User()
        user.name = event['userName']
        user.id = event['request']['userAttributes']['sub']
        if user.id == None or user.name == None:
            raise Exception("Something went wrong!")
        user = user_handler.create_user(user, is_test, session)
        client = boto3.client('cognito-idp')
        client.admin_add_user_to_group(
            UserPoolId=event['userPoolId'],
            Username=user.name,
            GroupName='Detective'
        )

    return event
