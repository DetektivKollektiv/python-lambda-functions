import pytest
from moto import mock_ses
from moto.ses import ses_backend
import boto3
from uuid import uuid4
from sqlalchemy import func
from core_layer.db_handler import Session
from core_layer.model import Mail
from core_layer.model import Submission
from core_layer.handler.mail_handler import send_confirmation_mail


@pytest.fixture
def mail_id():
    return str(uuid4())

@pytest.fixture
def mail(mail_id):
    mail = Mail(id = mail_id,
                email = "test@test.de"
                )
    return mail

@pytest.fixture
def submission(mail_id):
    submission = Submission(id = str(uuid4()),
                            mail_id = mail_id,
                            submission_date = func.now()
                            )
    return submission

@mock_ses
def test_confirmation_mail(submission, mail, monkeypatch):
    
    monkeypatch.setenv("STAGE", "dev")

    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="no-reply@codetekt.org")

    with Session() as session:
        
        session.add_all([submission, mail])
        session.commit()

        send_confirmation_mail(submission.mail)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 1

        message = ses_backend.sent_messages[0]
        assert 'test@test.de' in message.destinations['ToAddresses']
        assert 'Bestätige deine Mail-Adresse' in message.body
        assert mail.id in message.body