import pytest
import boto3
import os
from moto import mock_ses, mock_stepfunctions
from core_layer.model.submission_model import Submission
from ....tests.helper import setup_scenarios
from core_layer.model.item_model import Item
from core_layer.model.mail_model import Mail
from core_layer.db_handler import Session
from submission_service.submit_item import submit_item

# First item
@pytest.fixture
def event1():
    return {
        "body": {
            "content": "Test item",
            "item_type_id": "Type1",
            "mail": "test1@test.de",
            "item": {
                "content": "Test item",
                "id": "122212",
                "language": ""
            }

        },
        "requestContext": {
            "identity": {
                "sourceIp": "1.2.3.4"
            }
        }
    }

# Second item, same content as first one
@pytest.fixture
def event2():
    return {
        "body": {
            "content": "Test item",
            "item_type_id": "Type1",
            "mail": "test2@test.de",
            "item": {
                "content": "Test item",
                "id": "122212",
                "language": ""
            }
        },
        "requestContext": {
            "identity": {
                "sourceIp": "2.3.4.5"
            }
        }
    }

# Confirmed mail address
@pytest.fixture
def confirmed_mail_address():
    mail = Mail(id="1234",
                email="mail@domain.com",
                status="confirmed"
                )
    return mail

# Third item
@pytest.fixture
def event_item_with_confirmed_mail_address(confirmed_mail_address):
    return {
        "body": {
            "content": "Item with confirmed mail address",
            "item_type_id": "Type1",
            "mail": confirmed_mail_address.email,
            "item": {
                "content": "Item with confirmed mail address",
                "id": "122213",
                "language": ""
            }

        },
        "requestContext": {
            "identity": {
                "sourceIp": "3.4.5.6"
            }
        }
    }


def test_submit_item(event1, event2, event_item_with_confirmed_mail_address, confirmed_mail_address, monkeypatch):

    # Set environment variable
    monkeypatch.setenv("STAGE", "dev")
    monkeypatch.setenv("MOTO_ACCOUNT_ID", "891514678401")
    os.environ["MOTO"] = ""
    with mock_stepfunctions(), mock_ses():
        # Initialize mock clients
        sf_client = boto3.client("stepfunctions", region_name="eu-central-1")
        sf_client.create_state_machine(
            name="SearchFactChecks_new-dev",
            definition="{}",
            roleArn="arn:aws:iam::891514678401:role/detektivkollektiv-stepfunct-StateMachineLambdaRole"
        )
        ses_client = boto3.client("ses", region_name="eu-central-1")
        ses_client.verify_email_identity(EmailAddress="no-reply@codetekt.org")

        with Session() as session:

            session = setup_scenarios.create_questions(session)
            # Create confirmed mail
            session.add(confirmed_mail_address)
            session.commit()

            # Submit first item
            response = submit_item(event1, None)

            assert response["statusCode"] == 201
            assert response["headers"]["new-item-created"] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            assert session.query(Submission.ip_address).first()[0] == "1.2.3.4"
            assert session.query(Submission).first(
            ).mail.email == "test1@test.de"

            # Submit second item with same content as first one
            submit_item(event2, None)

            # Check database entries
            assert session.query(Item).count() == 1  # items didn"t increase
            # submissions increased
            assert session.query(Submission).count() == 2
            first_item_id = session.query(Item.id).first()[0]
            assert session.query(Item.submissions).\
                filter(Item.id == first_item_id).count(
            ) == 2  # number of submissions to first item increased
            # ip address of second submission assigned to first item
            assert session.query(Submission.ip_address).all()[
                1][0] == "2.3.4.5"

            # Submit item with confirmed mail address -> confirmation mail should not be sent
            submit_item(event_item_with_confirmed_mail_address, None)
            assert session.query(Item).count() == 2
            assert session.query(Submission).count() == 3

            # Check if mail addresses were added to DB
            assert session.query(Mail).count() == 3

            # Check if confirmation mails have been sent
            send_quota = ses_client.get_send_quota()
            sent_count = int(send_quota["SentLast24Hours"])
            assert sent_count == 4  # Recipients and BCC
            from moto.ses import ses_backend
            for message_id, sent_message in enumerate(ses_backend.sent_messages):
                mail_id = session.query(Mail).filter(Mail.status!='confirmed').all()[message_id].id
                assert mail_id in sent_message.body
                assert f"https://api.dev.codetekt.org/user_service/mails/{mail_id}/confirm" in sent_message.body
                assert "Bestätige deine Mail-Adresse" in sent_message.body


def test_remove_control_characters_1():
    from submission_service.submit_item import remove_control_characters

    s = remove_control_characters("Solange der CT Wert beim PCR Test nicht berücksichtigt wird, sind die Zahlen nix Wert und treiben lediglich die \"Statistik\" in die Höhe. Der einzige Grund warum der CT Wert nicht ermittelt wird, ist, dass die Einschränkungen der Bürger incl. Gesetzesänderung, weiter vorangetrieben werden sollen.")

    assert s == "Solange der CT Wert beim PCR Test nicht berücksichtigt wird, sind die Zahlen nix Wert und treiben lediglich die  Statistik  in die Höhe. Der einzige Grund warum der CT Wert nicht ermittelt wird, ist, dass die Einschränkungen der Bürger incl. Gesetzesänderung, weiter vorangetrieben werden sollen."
