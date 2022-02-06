import pytest
from core_layer.model.item_model import Item
from core_layer.model.mail_model import Mail
from core_layer.model.submission_model import Submission
from notification_service.src import item_rejected_handler
from uuid import uuid4
from core_layer.db_handler import Session
import boto3
from moto import mock_ses, mock_stepfunctions
import os


@pytest.fixture
def item_id():
    return str(uuid4())

@pytest.fixture
def mail_id():
    return str(uuid4())

@pytest.fixture
def item(item_id):
    item = Item(id = item_id,
                result_score = 3.4,
                content = 'testcontent')
    return item

@pytest.fixture
def mail(mail_id):
    mail = Mail(id = mail_id,
                email = "mail@domain.com",
                status = 'confirmed'
                )
    return mail

@pytest.fixture
def submission(item_id, mail_id):
    submission = Submission(id = str(uuid4()),
                            item_id = item_id,
                            mail_id = mail_id)
    return submission

@pytest.fixture
def event(item_id):
    return {"detail": {"item_id": item_id}}



def test_item_closed(item, mail, submission, event, monkeypatch):

    # Set environment variable
    os.environ["MOTO"] = ""
    with mock_stepfunctions(), mock_ses():
        # Initialize mock clients
        ses_client = boto3.client("ses", region_name = "eu-central-1")
        ses_client.verify_email_identity(EmailAddress = "no-reply@codetekt.org")

        with Session() as session:
            session.add_all([item, mail, submission])
            session.commit()

            response = item_rejected_handler.handle_item_rejected(event, None)
            assert response['statusCode'] == 200

            # Check notification mail
            send_quota = ses_client.get_send_quota()
            sent_count = int(send_quota["SentLast24Hours"])
            assert sent_count == 1
            from moto.ses import ses_backend
            sent_messages = ses_backend.sent_messages
            item.id in sent_messages[0].body
            "Dein Fall wurde abgelehnt!" in sent_messages[0].body


def test_no_item_id(monkeypatch):
    event = {}

    response = item_rejected_handler.handle_item_rejected(event, None)
    assert response['statusCode'] == 400


def test_wrong_item_id(monkeypatch):
    event = {"detail": {"item_id": "e9e376b5-0444-4eff-a7af-a3189ba2291e"}}
    response = item_rejected_handler.handle_item_rejected(event, None)
    assert response['statusCode'] == 400