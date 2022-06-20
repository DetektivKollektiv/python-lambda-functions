import pytest
import boto3
import os
from core_layer.db_handler import Session
from user_service import mail_subscription
from core_layer.model.mail_model import Mail
from moto import mock_ses
from core_layer.handler import mail_handler

from core_layer.test.helper.fixtures import database_fixture

@pytest.fixture
def mail_address():
    return "mail@provider.com"


@mock_ses
def test_double_opt_in(mail_address, monkeypatch, database_fixture):

    # mock required stuff
    monkeypatch.setenv("STAGE", "dev")
    os.environ["MOTO"] = ""
    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="no-reply@codetekt.org")

    with Session() as session:

        # Add mail address to DB and send verificiation mail
        mail = Mail()
        mail.email = mail_address
        mail_handler.create_mail(mail, session)
        mail_handler.send_confirmation_mail(mail)

        # Check verification mail
        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 2  # Recipient and BCC
        from moto.ses import ses_backends
        message = ses_backends["global"].sent_messages[0]
        assert mail_address in message.destinations['ToAddresses']
        assert 'Bestätige deine Mail-Adresse' in message.body
        assert mail.id in message.body

        # Confirm subscription
        event = {'pathParameters': {'mail_id': mail.id}}
        response = mail_subscription.confirm_mail_subscription(
            event, context="")

        # Check response
        assert response['statusCode'] == 200
        assert 'Mail-Adresse erfolgreich bestätigt!' in response['body']
        assert 'https://dev.codetekt.org' in response['body']
        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 2  # Recipient and BCC
