import pytest
import json
import boto3
from core_layer.model.submission_model import Submission
from ....tests.helper import event_creator, setup_scenarios
from core_layer.model.item_model import Item
from core_layer.connection_handler import get_db_session
from submission_service.submit_item import submit_item

# First item so submit


@pytest.fixture
def event1():
    return {
        'body': {
            "content": "Test item",
            "item_type_id": "Type1",
            "mail": "test1@test.de"

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
            "item_type_id": "Type1",
            "mail": "test2@test.de"
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


def test_submit_item(session, event1, event2, monkeypatch):
    # Set environment variable
    monkeypatch.setenv("STAGE", "dev")
    monkeypatch.setenv("MOTO_ACCOUNT_ID", '891514678401')
    from moto import mock_ses, mock_stepfunctions
    with mock_stepfunctions(), mock_ses():
        # Initialize mock clients
        sf_client = boto3.client('stepfunctions', region_name="eu-central-1")
        sf_client.create_state_machine(
            name='SearchFactChecks_new-dev',
            definition='{}',
            roleArn='arn:aws:iam::891514678401:role/detektivkollektiv-stepfunct-StateMachineLambdaRole'
        )
        ses_client = boto3.client("ses", region_name="eu-central-1")
        ses_client.verify_email_identity(EmailAddress="no-reply@codetekt.org")
        # Submit item
        response = submit_item(event1, None, True, session)

        assert response['statusCode'] == 201
        assert response['headers']['new-item-created'] == "True"

        # Check database entries
        assert session.query(Item).count() == 1
        assert session.query(Submission).count() == 1
        assert session.query(Submission.ip_address).first()[0] == '1.2.3.4'

        # Submit same item again
        submit_item(event2, None, True, session)
        # Check database entries
        assert session.query(Item).count() == 1  # items didn't increase
        assert session.query(Submission).count() == 2  # submissions increased
        first_item_id = session.query(Item.id).first()[0]
        assert session.query(Item.submissions).\
            filter(Item.id == first_item_id).count(
        ) == 2  # number of submissions to first item increased
        # ip address of second submission assigned to first item
        assert session.query(Submission.ip_address).all()[1][0] == '2.3.4.5'
        # Check if confirmation mails have been sent
        send_quota = ses_client.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        assert sent_count == 2
