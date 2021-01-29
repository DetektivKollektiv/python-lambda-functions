from moto import mock_ses
from moto.ses import ses_backend
from moto.ses.models import Message
import boto3
from botocore.exceptions import ClientError
import pytest
from uuid import uuid4
from core_layer.model import Item, Submission
from core_layer.connection_handler import get_db_session
from submission_service.confirm_submission import confirm_submission


@pytest.fixture
def item():
    item = Item()
    item.id = str(uuid4())
    item.content = "Test"
    item.result_score = 1.000
    return item


@pytest.fixture
def submission_id():
    return str(uuid4())


@pytest.fixture
def session(item, submission_id):
    session = get_db_session(True, None)

    submission = Submission()
    submission.id = submission_id
    submission.mail = "test@test.de"
    submission.item = item

    session.add(item)
    session.add(submission)
    session.commit()

    return session


@mock_ses
def test_mail_notification(session, item, submission_id):
    from review_service import notifications

    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="info@detektivkollektiv.org")

    notifications.notify_users(True, session, item)

    send_quota = conn.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 0

    event = {
        'pathParameters': {
            'submission_id': submission_id
        }
    }
    confirm_submission(event, None, True, session)

    notifications.notify_users(True, session, item)

    send_quota = conn.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 1

    message = ses_backend.sent_messages[0]
    assert 'test@test.de' in message.destinations['ToAddresses']
    assert 'Dein Fall wurde gelöst' in message.body
    assert '1.0' in message.body
    assert 'nicht vertrauenswürdig' in message.body


# Use this to send a confirmation email to your adress
def test_mail_confirmation(session, submission_id, monkeypatch):
    monkeypatch.setenv("STAGE", "dev")
    from submission_service import submit_item
    submission = session.query(Submission).filter(
        Submission.id == submission_id).one()
    # Add you mail adress here in local testing mode
    submission.mail = "test@test.de"
    session.merge(submission)
    session.commit()
    submit_item.send_confirmation_mail(submission)
