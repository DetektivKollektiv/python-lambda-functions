from moto import mock_ses
from moto.ses import ses_backend
import boto3
import pytest
from uuid import uuid4
from core_layer.model import Item, Submission
from core_layer.db_handler import Session
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


@mock_ses
def test_mail_notification(item, submission_id, monkeypatch):
    monkeypatch.setenv("STAGE", "dev")
    from review_service import notifications

    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="no-reply@codetekt.org")

    with Session() as session:

        submission = Submission()
        submission.id = submission_id
        submission.mail = "test@test.de"
        submission.item = item

        session.add(item)
        session.add(submission)
        session.commit()

        notifications.notify_users(session, item)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 0

        event = {
            'pathParameters': {
                'submission_id': submission_id
            }
        }
        response = confirm_submission(event, None)
        assert response['statusCode'] == 200
        assert response['headers']['content-type'] == 'text/html; charset=utf-8'
        assert 'Mail-Adresse erfolgreich bestätigt!' in response['body']
        assert 'https://dev.codetekt.org' in response['body']

        notifications.notify_users(session, item)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 1

        message = ses_backend.sent_messages[0]
        assert 'test@test.de' in message.destinations['ToAddresses']
        assert 'Dein Fall wurde gel&ouml;st' in message.body
        assert '1.0' in message.body
        assert 'nicht vertrauenswürdig' in message.body


# Use this to send a confirmation email to your adress
def test_mail_confirmation(submission_id, item, monkeypatch):
    monkeypatch.setenv("STAGE", "dev")
    from submission_service import submit_item

    with Session() as session:

        submission = Submission()
        submission.id = submission_id
        submission.mail = "test@test.de"
        submission.item = item
        
        session.add(item)
        session.add(submission)
        session.commit()
        
        submission = session.query(Submission).filter(
            Submission.id == submission_id).one()
        # Add your mail address here in local testing mode
        submission.mail = "test@test.de"
        
        session.merge(submission)
        session.commit()
        submit_item.send_confirmation_mail(submission)        
