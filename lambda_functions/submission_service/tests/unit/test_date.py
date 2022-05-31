from core_layer.model.item_type_model import ItemType
import pytest
from core_layer.model.submission_model import Submission
from core_layer.db_handler import Session
from submission_service.submit_item import submit_item
import boto3


@pytest.fixture
def event1():
    return {
        'body': {
            "content": "Test item",
            "item_type_id": "1",
            "mail": "test1@test.de"

        },
        'requestContext': {
            'identity': {
                'sourceIp': '1.2.3.4'
            }
        }
    }


def test_dates(event1, monkeypatch):
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

    with Session() as session:
        monkeypatch.setenv("STAGE", "dev")

        session.add(ItemType(id='1'))
        submissions = session.query(Submission).all()
        response = submit_item(event1, None)
        assert response['statusCode'] == 201
        assert 1 == 1
