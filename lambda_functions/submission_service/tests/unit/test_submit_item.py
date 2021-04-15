import pytest
from moto import mock_ses
from moto.ses import ses_backend
from moto.ses.models import Message
import boto3
from core_layer.model import Submission
from uuid import uuid4
from sqlalchemy import func
from core_layer.connection_handler import get_db_session


@pytest.fixture
def submission():
    submission = Submission()
    submission.id = str(uuid4())
    submission.mail = "test@test.de"
    submission.submission_date = func.now()
    return submission


@pytest.fixture
def session(submission):
    session = get_db_session(True, None)
    session.add(submission)
    session.commit()
    return session


@mock_ses
def test_send_confirmation_mail(session, submission, monkeypatch):
    from submission_service.submit_item import send_confirmation_mail
    monkeypatch.setenv("STAGE", "dev")

    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="no-reply@codetekt.org")

    send_confirmation_mail(submission)

    send_quota = conn.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 1

    message = ses_backend.sent_messages[0]
    assert 'test@test.de' in message.destinations['ToAddresses']
    assert 'Bestätige deine Mail-Adresse' in message.body
    assert submission.id in message.body
