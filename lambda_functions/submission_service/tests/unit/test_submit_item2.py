import os
import pytest
import boto3
from core_layer.model.submission_model import Submission
from core_layer.model.item_model import Item
from core_layer.db_handler import Session
from core_layer.helper import get_google_api_key
from submission_service.submit_item import submit_item
from ....tests.helper import setup_scenarios

from core_layer.test.helper.fixtures import database_fixture

def create_event1():
    return create_event_body("Wollen wir auch einen Channel für solche Themen anlegen?\
                           https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf\
                           -desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57\
                           ?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ")

def create_event2():
    return create_event_body("Wollen wir auch einen Channel für solche Themen anlegen? \
            https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf \
            -desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57 \
            ?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ\n"
            "Und jetzt noch eine böse URL: http://testsafebrowsing.appspot.com/s/malware.html")

def create_event3():
    return create_event_body("Ein Link ohne http/s www.compact-online.de/utes-moma-2-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen-die-corona-regeln")

##############################################################################################
# Because the boto3 client is mocked in the tests,                                           #
# the get_secret() for receiving the GOOGLE API KEY would return 'None'.                     #
# Solution: get_secret() is called in advance and the key is exposed as an environment value #
##############################################################################################
os.environ["UNITTEST_GOOGLE_API_KEY"] = get_google_api_key()

@pytest.mark.skip("Test doesn't run when called through pytest")
def test_submit_safe_item(monkeypatch, database_fixture):
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
            response = submit_item(create_event1(), None)

            assert response['statusCode'] == 201
            assert response['headers']['new-item-created'] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            submission = session.query(Submission).first()
            assert submission.mail.email == 'test@test.de'
            assert session.query(Submission.ip_address).first()[0] == '1.2.3.4'


def test_submit_unsafe_item(monkeypatch, database_fixture):
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
            response = submit_item(create_event2(), None)

            assert response['statusCode'] == 403
            assert response['headers']['new-item-created'] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            submission = session.query(Submission).first()
            assert submission.mail.email == 'test@test.de'
            assert submission.item.urls[0].url.unsafe is None
            assert submission.item.urls[1].url.unsafe == "GOOGLE:MALWARE"


@pytest.mark.skip("Test doesn't run when called through pytest")
def test_submit_content_with_url_without_http(monkeypatch, database_fixture):
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

        ses_client = boto3.client("ses", region_name="eu-central-1")

        with Session() as session:
            session = setup_scenarios.create_questions(session)

            # Submit first item
            response = submit_item(create_event3(), None)

            assert response['statusCode'] == 201
            assert response['headers']['new-item-created'] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            submission = session.query(Submission).first()
            assert submission.mail.email == 'test@test.de'
            assert len(submission.item.urls) == 0

def create_event_body(content):
    return {
        'body': {
            "content": content,
            "item_type_id": "Type1",
            "mail": "test@test.de",
            "item": {
                "content": content,
                "id": "122212",
                "language": ""
            }
        },
        'requestContext': {
            'identity': {
                'sourceIp': '1.2.3.4'
            }
        }
    }