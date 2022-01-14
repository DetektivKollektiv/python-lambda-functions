import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from user_service.create_user import create_user
from core_layer.model.level_model import Level
from moto import mock_cognitoidp
import boto3
import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from core_layer.model.mail_model import Mail
from core_layer.model.user_model import User


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
def event(user_id, user_name, mail_address):
    event = {
             "triggerSource": "PostConfirmation_ConfirmSignUp",
             "userName": user_name,
             "request":
                 {
                     "userAttributes": {
                         "email": mail_address,
                         "sub": user_id
                     }
                 }
            }
    return event


@mock_cognitoidp
def test_create_user(event, user_name, mail_address):


    # mocking stuff that's required
    cognitoidp = boto3.client("cognito-idp", region_name = "eu-central-1")

    response = cognitoidp.create_user_pool(PoolName = "PoolNameString")
    user_pool_id = response['UserPool']['Id']
    event['userPoolId'] = user_pool_id # add user_pool_id to event as it's requested from there by admin_add_user_to_group method

    cognitoidp.create_group(GroupName = 'Detective',
                            UserPoolId = user_pool_id
                            )
    cognitoidp.admin_create_user(UserPoolId = user_pool_id,
                           Username = user_name
                           )


    with Session() as session:

        level_1_obj = Level(id = 1)
        session.add_all([level_1_obj])
        session.commit()    
        create_user(event)

        # Check if user and mail is created
        assert session.query(User).first().name == user_name
        assert session.query(Mail).first().email == mail_address