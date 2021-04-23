import pytest
import json
from core_layer.model.submission_model import Submission
from ....tests.helper import event_creator, setup_scenarios
from moto import mock_ses
from core_layer.model.item_model import Item
from core_layer.connection_handler import get_db_session
from submission_service.submit_item import submit_item

# First item so submit
@pytest.fixture
def event1():
    return {
        'body': {
            "content": "Test item",
            "item_type_id": "Type1"
            },
        'requestContext': {
            'identity': {
                'sourceIp': '1.2.3.4'
            }
    }
    }

# Second item to submit, same content as first one
@pytest.fixture
def event2():
    return {
        'body': {
            "content": "Test item",
            "item_type_id": "Type1"
            },
        'requestContext': {
            'identity': {
                'sourceIp': '2.3.4.5'
            }
    }
    }

@pytest.fixture
def session():
    session = get_db_session(True, None)
    session = setup_scenarios.create_questions(session)

    return session


@mock_ses
def test_submit_item(session, event1, event2, monkeypatch):
    # Set environment variable
    monkeypatch.setenv("STAGE", "dev") 
    
    # Submit item
    submit_item(event1, None, True, session)
    # Check database entries
    assert session.query(Item).count() == 1
    assert session.query(Submission).count() == 1
    assert session.query(Submission.ip_address).first()[0] == '1.2.3.4'

    # Submit same item again
    submit_item(event2, None, True, session)
    # Check database entries
    assert session.query(Item).count() == 1 # items didn't increase
    assert session.query(Submission).count() == 2 # submissions increased
    first_item_id = session.query(Item.id).first()[0]
    assert session.query(Item.submissions).\
           filter(Item.id == first_item_id).count() == 2 # number of submissions to first item increased
    assert session.query(Submission.ip_address).all()[1][0] == '2.3.4.5' # ip address of second submission assigned to first item
