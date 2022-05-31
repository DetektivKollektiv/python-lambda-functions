import pytest
from core_layer.model.item_model import Item
from core_layer.model.mail_model import Mail
from core_layer.model.submission_model import Submission
from notification_service.src import item_closed_handler
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
    item = Item(id=item_id,
                result_score=3.4,
                content='testcontent')
    return item


@pytest.fixture
def mail(mail_id):
    mail = Mail(id=mail_id,
                email="mail@domain.com",
                status='confirmed'
                )
    return mail


@pytest.fixture
def submission(item_id, mail_id):
    submission = Submission(id=str(uuid4()),
                            item_id=item_id,
                            mail_id=mail_id)
    return submission


@pytest.fixture
def event(item_id):
    return {"detail": {"item_id": item_id}}


def test_item_closed(item, mail, submission, event, monkeypatch):

    # Set environment variable
    monkeypatch.setenv("STAGE", "dev")
    os.environ["MOTO"] = ""
    with mock_stepfunctions(), mock_ses():
        # Initialize mock clients
        ses_client = boto3.client("ses", region_name="eu-central-1")
        ses_client.verify_email_identity(EmailAddress="no-reply@codetekt.org")

        with Session() as session:
            session.add_all([item, mail, submission])
            session.commit()

            response = item_closed_handler.handle_item_closed(event, None)
            assert response['statusCode'] == 200

            # Check notification mail
            send_quota = ses_client.get_send_quota()
            sent_count = int(send_quota["SentLast24Hours"])
            assert sent_count == 2
            from moto.ses import ses_backend
            sent_messages = ses_backend.sent_messages
            item.id in sent_messages[0].body
            "Dein Fall wurde gelöst!" in sent_messages[0].body
            assert f"https://api.dev.codetekt.org/user_service/mails/{submission.mail.id}/unsubscribe" in sent_messages[
                0].body


def test_no_item_id(monkeypatch):
    event = {}

    response = item_closed_handler.handle_item_closed(event, None)
    # response_dict = json.loads(response)
    assert response['statusCode'] == 400


def test_wrong_item_id(monkeypatch):
    event = {"detail": {"item_id": "e9e376b5-0444-4eff-a7af-a3189ba2291e"}}

    response = item_closed_handler.handle_item_closed(event, None)
    assert response['statusCode'] == 400


testdata = [
    (1, "nicht vertrauenswürdig"),
    (40, "eher nicht vertrauenswürdig"),
    (83, "eher vertrauenswürdig"),
    (84, "vertrauenswürdig")
]


@pytest.mark.parametrize("input, expected", testdata)
def test_get_rating_text(input: float, expected: str):

    rating_text = item_closed_handler.get_rating_text(input)

    assert rating_text == expected
