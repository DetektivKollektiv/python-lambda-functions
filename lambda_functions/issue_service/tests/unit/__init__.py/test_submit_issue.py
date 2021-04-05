import pytest
from uuid import uuid4
from moto import mock_ses
from moto.ses import ses_backend
from moto.ses.models import Message
import boto3
from core_layer.model.issue_model import Issue
from core_layer.model.item_model import Item
from core_layer.connection_handler import get_db_session


@pytest.fixture
def item():
    item = Item()
    item.id = str(uuid4())
    item.content = 'Test item'
    return item


@pytest.fixture
def good_event():
    return {
        'body': {
            'category': 'Feedback',
            'message': 'Good Job'
        },
        'requestContext': {
            'identity': {
                'sourceIp': '1.2.3.4'
            }
    }
    }


@pytest.fixture
def bad_event():
    return {
        'body': {
            'NotAnAttribute': 'Feedback',
            'message': 'Good Job'
        }
    }


@pytest.fixture
def item_event(item):
    return {
        'body': {
            'category': 'Complaint',
            'message': 'This item violates my rights',
            'item_id': item.id
        }
    }


@pytest.fixture
def session(item):
    session = get_db_session(True, None)
    session.add(item)
    session.commit()
    return session


@mock_ses
def test_submit_issue(session, good_event, bad_event, item_event, item):
    from issue_service.submit_issue import submit_issue
    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="info@detektivkollektiv.org")
    # Send good event
    response = submit_issue(good_event, None, True, session)
    # Check response
    assert response['statusCode'] == 201
    assert good_event['body']['message'] in response['body']
    # Check e-mail notification
    send_quota = conn.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 1
    message = ses_backend.sent_messages[0]
    assert 'info@detektivkollektiv.org' in message.destinations['ToAddresses']
    assert good_event['body']['message'] in message.body
    # Check database entry
    issue_count = session.query(Issue).count()
    issue = session.query(Issue).first()
    assert issue.ip_address == '1.2.3.4'
    assert issue_count == 1

    # Send bad event
    response = submit_issue(bad_event, None, True, session)
    # Check response
    assert response['statusCode'] == 400
    # Check e-mail notification
    send_quota = conn.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 1
    # Check database entry
    issue_count = session.query(Issue).count()
    assert issue_count == 1

    # Send item event
    response = submit_issue(item_event, None, True, session)
    # Check response
    assert response['statusCode'] == 201
    assert item_event['body']['message'] in response['body']
    # Check e-mail notification
    send_quota = conn.get_send_quota()
    sent_count = int(send_quota["SentLast24Hours"])
    assert sent_count == 2
    message = ses_backend.sent_messages[1]
    assert 'info@detektivkollektiv.org' in message.destinations['ToAddresses']
    assert item_event['body']['message'] in message.body
    assert item.id in message.body
    assert item.content in message.body
    # Check database entry
    issue_count = session.query(Issue).count()
    assert issue_count == 2