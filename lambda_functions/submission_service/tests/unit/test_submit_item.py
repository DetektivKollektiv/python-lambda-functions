import pytest
import boto3
from core_layer.model.submission_model import Submission
from ....tests.helper import setup_scenarios
from core_layer.model.item_model import Item
from core_layer.db_handler import Session
from submission_service.submit_item import submit_item

# First item
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

# Second item, same content as first one
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


def test_submit_item(event1, event2, monkeypatch):
    
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

        with Session() as session:

            session = setup_scenarios.create_questions(session)

            # Submit first item
            response = submit_item(event1, None)

            assert response['statusCode'] == 201
            assert response['headers']['new-item-created'] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            assert session.query(Submission.ip_address).first()[0] == '1.2.3.4'

            # Submit second item with same content as first one
            submit_item(event2, None)
            # Check database entries
            assert session.query(Item).count() == 1  # items didn't increase
            assert session.query(Submission).count() == 2  # submissions increased
            first_item_id = session.query(Item.id).first()[0]
            assert session.query(Item.submissions).\
                filter(Item.id == first_item_id).count() == 2  # number of submissions to first item increased
            assert session.query(Submission.ip_address).all()[1][0] == '2.3.4.5' # ip address of second submission assigned to first item
            # Check if confirmation mails have been sent
            send_quota = ses_client.get_send_quota()
            sent_count = int(send_quota["SentLast24Hours"])
            assert sent_count == 2

def test_remove_control_characters_1():
    from submission_service.submit_item import remove_control_characters

    s = remove_control_characters("Solange der CT Wert beim PCR Test nicht berücksichtigt wird, sind die Zahlen nix Wert und treiben lediglich die \"Statistik\" in die Höhe. Der einzige Grund warum der CT Wert nicht ermittelt wird, ist, dass die Einschränkungen der Bürger incl. Gesetzesänderung, weiter vorangetrieben werden sollen.")

    assert s == 'Solange der CT Wert beim PCR Test nicht berücksichtigt wird, sind die Zahlen nix Wert und treiben lediglich die  Statistik  in die Höhe. Der einzige Grund warum der CT Wert nicht ermittelt wird, ist, dass die Einschränkungen der Bürger incl. Gesetzesänderung, weiter vorangetrieben werden sollen.'
