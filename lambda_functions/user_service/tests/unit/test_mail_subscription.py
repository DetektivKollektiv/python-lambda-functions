from user_service.mail_subscription import unsubscribe_mail
import pytest
from uuid import uuid4
from core_layer.model import User
from core_layer.db_handler import Session
from core_layer.model.mail_model import Mail
from core_layer.model.level_model import Level

from moto import mock_ses
from moto.ses import ses_backend
import boto3

@pytest.fixture
def user_id():
    return str(uuid4())

@pytest.fixture
def mail_id():
    return str(uuid4())

@pytest.fixture
def event(user_id):
    return {
        'pathParameters': {
            'user_id': user_id
        }
    }

@mock_ses
def test_mail_subscription(user_id, mail_id, event, monkeypatch):

    # Set environment variable
    monkeypatch.setenv("STAGE", "dev")

    with Session() as session:
              
        # Create User object
        user_obj = User(id = user_id)
        level_obj = Level(id = 1)
        # Create Mail object
        mail_obj = Mail(id = mail_id,
                        user_id = user_id,
                        status = 'confirmed')
        session.add_all([user_obj, level_obj, mail_obj])
        session.commit()

        unsubscribe_mail(event)
        assert session.query(Mail).first().status == "unsubscribed"