import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from user_service.create_user import create_user
from core_layer.model.level_model import Level
from core_layer.model.mail_model import Mail
from core_layer.model.user_model import User
from moto import mock_cognitoidp, mock_ses
import boto3


@pytest.fixture
def user_id():
    return str(uuid4())

@pytest.fixture
def user_name():
    return "Max Muster"

@pytest.fixture
def mail_address():
    return "mail@provider.com"

@pytest.fixture
def event_mail_subscription_0(user_id, user_name, mail_address):
    event = {
             "triggerSource": "PostConfirmation_ConfirmSignUp",
             "userName": user_name,
             "request":
                 {
                     "userAttributes": {
                         "email": mail_address,
                         "sub": user_id,
                         "custom:mail_subscription": '0'
                     }
                 }
            }
    return event

@pytest.fixture
def event_mail_subscription_1():
    event = {
             "triggerSource": "PostConfirmation_ConfirmSignUp",
             "userName": "user_name2",
             "request":
                 {
                     "userAttributes": {
                         "email": "mail2@provider.com",
                         "sub": str(uuid4()),
                         "custom:mail_subscription": '1'
                     }
                 }
            }
    return event

@pytest.fixture
def event_without_mail_subscription_status():
    event = {
             "triggerSource": "PostConfirmation_ConfirmSignUp",
             "userName": "user_name3",
             "request":
                 {
                     "userAttributes": {
                         "email": "mail3@provider.com",
                         "sub": str(uuid4())
                     }
                 }
            }
    return event


@mock_ses
@mock_cognitoidp
def test_create_user(event_mail_subscription_0, event_mail_subscription_1, event_without_mail_subscription_status, user_name, mail_address, monkeypatch):


    # mock required stuff

    monkeypatch.setenv("STAGE", "dev")

    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="no-reply@codetekt.org")

    cognitoidp = boto3.client("cognito-idp", region_name = "eu-central-1")

    # add user_pool_id to event as it's requested from there by admin_add_user_to_group method
    for event in [event_mail_subscription_0, event_mail_subscription_1, event_without_mail_subscription_status]:
        response = cognitoidp.create_user_pool(PoolName = "PoolNameString")
        user_pool_id = response['UserPool']['Id']
        event['userPoolId'] = user_pool_id 
        cognitoidp.create_group(GroupName = 'Detective',
                                UserPoolId = user_pool_id
                                )
        cognitoidp.admin_create_user(UserPoolId = user_pool_id,
                                     Username = event['userName']
                                     )


    with Session() as session:

        level_1_obj = Level(id = 1)
        session.add_all([level_1_obj])
        session.commit()
        create_user(event_mail_subscription_0)

        # Check if user and mail is created
        user = session.query(User).first()
        assert user.name == user_name
        assert user.mail.email == mail_address
        mail = session.query(Mail).first()
        assert mail.status == 'unsubscribed'

        # Check cases with other "custom:mail_subscription" attributes
        create_user(event_mail_subscription_1)
        mail = session.query(Mail).all()[1]
        assert mail.status == 'confirmed'

        create_user(event_without_mail_subscription_status)
        mail = session.query(Mail).all()[2]
        assert mail.status == 'unsubscribed'