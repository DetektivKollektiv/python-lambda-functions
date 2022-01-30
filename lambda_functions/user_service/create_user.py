import boto3
import logging
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.model.user_model import User
from core_layer.model.mail_model import Mail
from core_layer.handler import user_handler, mail_handler


def create_user(event):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Create user from cognito", event, logger)

    with Session() as session:

        if event['triggerSource'] == "PostConfirmation_ConfirmSignUp":
            user = User()
            user.name = event['userName']
            user.id = event['request']['userAttributes']['sub']
            if user.id == None or user.name == None:
                raise Exception("Something went wrong!")
            user = user_handler.create_user(user, session)
            client = boto3.client('cognito-idp', region_name = "eu-central-1")
            client.admin_add_user_to_group(
                UserPoolId = event['userPoolId'],
                Username = user.name,
                GroupName = 'Detective'
            )

            # Add mail address if submitted
            if 'email' in event['request']['userAttributes']:
                mail = Mail()
                mail.email = event['request']['userAttributes']['email']
                mail.user_id = user.id
                mail_handler.create_mail(mail, session)
                if mail.status is not 'confirmed':
                    mail_handler.send_confirmation_mail(mail)

        return event