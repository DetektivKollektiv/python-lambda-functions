from user_service.mail_subscription import confirm_mail_subscription, unsubscribe_mail
import pytest
from uuid import uuid4
from core_layer.model import User
from core_layer.db_handler import Session
from core_layer.model.mail_model import Mail
from core_layer.model.level_model import Level


@pytest.fixture
def user_id():
    return str(uuid4())

@pytest.fixture
def mail_id():
    return str(uuid4())

@pytest.fixture
def event(mail_id):
    return {
        'pathParameters': {
            'mail_id': mail_id
        }
    }

@pytest.fixture
def event_with_wrong_mail_id():
    return {
        'pathParameters': {
            'mail_id': str(uuid4())
        }
    }

def test_mail_subscription(user_id, mail_id, event, event_with_wrong_mail_id, monkeypatch):

    # Set environment variable
    monkeypatch.setenv("STAGE", "dev")

    with Session() as session:
              
        # Create User object
        user_obj = User(id = user_id, mail_id = mail_id)
        level_obj = Level(id = 1)
        # Create Mail object
        mail_obj = Mail(id = mail_id)
        session.add_all([user_obj, level_obj, mail_obj])
        session.commit()

        # Check mail status
        assert session.query(Mail).first().status == "unconfirmed"
        # Confirm subscription
        confirm_mail_subscription(event, context = "")
        assert session.query(Mail).first().status == "confirmed"
        # Unsubscribe
        unsubscribe_mail(event, context = "")
        assert session.query(Mail).first().status == "unsubscribed"
        response = confirm_mail_subscription(event_with_wrong_mail_id, context = "")
        body = response['body']
        assert 'Deine Mail-Adresse konnte nicht bestätigt werden' in body