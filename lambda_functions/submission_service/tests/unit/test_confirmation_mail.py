from moto import mock_ses
from moto.ses import ses_backends
import pytest
import boto3
import os
from uuid import uuid4
from sqlalchemy import func
from core_layer.db_handler import Session
from core_layer.model import Mail
from core_layer.model import Submission
from core_layer.handler.mail_handler import send_confirmation_mail

from core_layer.test.helper.fixtures import database_fixture


@pytest.fixture
def mail_id():
    return str(uuid4())


@pytest.fixture
def mail(mail_id):
    mail = Mail(id=mail_id,
                email="test@test.de"
                )
    return mail


@pytest.fixture
def submission(mail_id):
    submission = Submission(id=str(uuid4()),
                            mail_id=mail_id,
                            submission_date=func.now()
                            )
    return submission


@mock_ses
def test_confirmation_mail(submission, mail, monkeypatch, database_fixture):

    monkeypatch.setenv("STAGE", "dev")
    os.environ["MOTO"] = ""

    conn = boto3.client("ses", region_name="eu-central-1")

    conn.verify_email_identity(EmailAddress="no-reply@codetekt.org")
    send_quota = conn.get_send_quota()

    with Session() as session:

        session.add_all([submission, mail])
        session.commit()

        send_confirmation_mail(submission.mail)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 2  # To recipient and BCC

        message = ses_backends["global"].sent_messages[0]
        assert 'test@test.de' in message.destinations['ToAddresses']
        assert 'Bestätige deine Mail-Adresse' in message.body
        assert mail.id in message.body
