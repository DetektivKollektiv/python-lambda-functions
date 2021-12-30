import pytest
from core_layer.model import Mail
from uuid import uuid4
from sqlalchemy import func
from datetime import timedelta, datetime
from core_layer.db_handler import Session
from core_layer import helper
from user_service.delete_unconfirmed_mails import delete_unconfirmed_mails
from user_service.create_user import create_user
from core_layer.model.level_model import Level

from moto import mock_ses, mock_cognitoidp
from moto.ses import ses_backend
import boto3
import pytest
from uuid import uuid4
from core_layer.model import Item, Submission
from core_layer.db_handler import Session


@pytest.fixture
def mail1():
    three_days_ago = helper.get_date_time(
        datetime.now() - timedelta(days=3))

    mail = Mail()
    mail.id = str(uuid4())
    mail.email = "Test_three_days_ago@test.de"
    mail.timestamp = three_days_ago
    mail.status = "unconfirmed"
    return mail

@pytest.fixture
def user_id():
    return str(uuid4())

@pytest.fixture
def mail_address():
    return "mail@provider.com"

@pytest.fixture
def event(user_id, mail_address):
    event = {
             "triggerSource": "PostConfirmation_ConfirmSignUp",
             "userPoolId": "string",
             "userName": "Max Muster",
             "request":
                 {
                     "userAttributes": {
                         "email": mail_address,
                         "sub": user_id
                     }
                 }
            }
    return event
 
@mock_ses
@mock_cognitoidp
def test_create_user(event, mail_address, user_id, monkeypatch):

    monkeypatch.setenv("STAGE", "dev")

    conn = boto3.client("ses", region_name = "eu-central-1")
    conn.verify_email_identity(EmailAddress = "no-reply@codetekt.org")

    with Session() as session:

        level_1_obj = Level(id = 1)
        session.add_all([level_1_obj])
        session.commit()
        create_user(event)