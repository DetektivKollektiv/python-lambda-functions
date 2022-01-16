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
def event(user_id):
    return {
        'pathParameters': {
            'user_id': user_id
        }
    }

def test_mail_subscription(user_id, mail_id, event, monkeypatch):

    # Set environment variable
    monkeypatch.setenv("STAGE", "dev")

    with Session() as session:
              
        # Create User object
        user_obj = User(id = user_id)
        level_obj = Level(id = 1)
        # Create Mail object
        mail_obj = Mail(id = mail_id, user_id = user_id)
        session.add_all([user_obj, level_obj, mail_obj])
        session.commit()

        # Check mail status
        assert session.query(Mail).first().status == "unconfirmed"
        # Confirm subscription
        confirm_mail_subscription(event)
        assert session.query(Mail).first().status == "confirmed"
        # Unsubscribe
        unsubscribe_mail(event)
        assert session.query(Mail).first().status == "unsubscribed"