import pytest
from uuid import uuid4
from moto import mock_ses
from moto.ses import ses_backends
import boto3
from core_layer.helper import body_to_object
from core_layer.model.issue_model import Issue
from core_layer.model.item_model import Item
from core_layer.db_handler import Session
from issue_service.submit_issue import submit_issue

from core_layer.test.helper.fixtures import database_fixture

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


def get_item(item_content='Test content'):
    item = Item()
    item.id = str(uuid4())
    item.content=item_content
    return item


def get_item_event(item, category='feedback', message='This is a feedback.'):
    return {
        'body': {
            'category': category,
            'message': message,
            'item_id': item.id
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


@mock_ses
def test_submit_issue(good_event, bad_event, database_fixture):
    
    conn = boto3.client("ses", region_name="eu-central-1")
    conn.verify_email_identity(EmailAddress="no-reply@codetekt.org")
    
    with Session() as session:  
        # Send good event
        response = submit_issue(good_event, None)
        # Check response
        assert response['statusCode'] == 201
        assert good_event['body']['message'] in response['body']
        # Check e-mail notification
        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 1
        message = ses_backends["global"].sent_messages[0]
        assert 'support@codetekt.org' in message.destinations['ToAddresses']
        assert good_event['body']['message'] in message.body
        # Check database entry
        issue_count = session.query(Issue).count()
        issue = session.query(Issue).first()
        assert issue.ip_address == '1.2.3.4'
        assert issue_count == 1
        
        # Send bad event
        response = submit_issue(bad_event, None)
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
        item = get_item('Content TestItem 111')
        session.add(item)
        session.commit() 

        item_event = get_item_event(item)
        response = submit_issue(item_event, None)
        
        # Check response
        assert response['statusCode'] == 201
        assert item_event['body']['message'] in response['body']
        issue = Issue()
        issue = body_to_object(response['body'], issue)
        assert issue.message == "This is a feedback."

        # Check e-mail notification
        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 2
        message = ses_backends["global"].sent_messages[1]
        assert 'support@codetekt.org' in message.destinations['ToAddresses']
        assert item_event['body']['message'] in message.body
        assert item.id in message.body
        assert item.content in message.body

        # Check database entry
        issue_count = session.query(Issue).count()
        assert issue_count == 2


        # Send item-event with another item
        item = get_item('Content TestItem 222')
        session.add(item)
        session.commit()
        item_event = get_item_event(item, 'complaint', 'This is a complaint.')
        response = submit_issue(item_event, None)       
        
        # Check response
        assert response['statusCode'] == 201
        assert item_event['body']['message'] in response['body']     
        issue = Issue()
        issue = body_to_object(response['body'], issue)
        assert issue.message == "This is a complaint." 

        # Check database entry
        issue_count = session.query(Issue).count()
        assert issue_count == 3
       