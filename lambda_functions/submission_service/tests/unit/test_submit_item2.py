import pytest
from uuid import uuid4
import boto3
from core_layer.model.submission_model import Submission
from core_layer.model.item_model import Item
from core_layer.model.url_model import URL, ItemURL
from core_layer.db_handler import Session
from core_layer.handler import item_handler
from submission_service.submit_item import submit_item
from ....tests.helper import setup_scenarios


def create_event1(session):
    return create_event_body("Wollen wir auch einen Channel für solche Themen anlegen?\
                           https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf\
                           -desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57\
                           ?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ")


def create_event2(session):
    return create_event_body("Wollen wir auch einen Channel für solche Themen anlegen? \
            https://www.spiegel.de/wissenschaft/mensch/corona-krise-und-klimawandel-fuenf \
            -desinformations-tricks-die-jeder-kennen-sollte-a-6892ff9b-fb28-43ae-8438-55b49d607e57 \
            ?sara_ecid=soci_upd_wbMbjhOSvViISjc8RPU89NcCvtlFcJ\n"
            "Und jetzt noch eine böse URL: http://testsafebrowsing.appspot.com/s/malware.html")

def create_event3(session):
    return create_event_body("Ein Link ohne http/s www.compact-online.de/utes-moma-2-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen-die-corona-regeln")


#### Caution: Because the boto3 client is mocked in the tests, the get_secret() call for receiving the google api key fails.
### To run the tests, set the Google API key in the url_threatcheck.py with the correct google api key.
### key = get_secret()  --> key = 'xxxxx'
###########################################
def test_submit_safe_item(monkeypatch):
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
            response = submit_item(create_event1(session), None)

            assert response['statusCode'] == 201
            assert response['headers']['new-item-created'] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            submission = session.query(Submission).first()
            assert submission.status != 'Unsafe'
            assert session.query(Submission.ip_address).first()[0] == '1.2.3.4'


def test_submit_unsafe_item(monkeypatch):
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
            response = submit_item(create_event2(session), None)

            assert response['statusCode'] == 403
            assert response['headers']['new-item-created'] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            submission = session.query(Submission).first()
            assert submission.status == 'Unsafe'
            assert submission.item.urls[0].unsafe is None
            assert submission.item.urls[1].unsafe == "GOOGLE:MALWARE"


def test_submit_content_with_url_without_http(monkeypatch):
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
            response = submit_item(create_event3(session), None)

            assert response['statusCode'] == 201
            assert response['headers']['new-item-created'] == "True"

            # Check database entries
            assert session.query(Item).count() == 1
            assert session.query(Submission).count() == 1
            submission = session.query(Submission).first()
            assert submission.status != 'Unsafe'
            assert len(submission.item.urls) == 0


def test_prepare_and_store_urls_without_https_protocol():
    with Session() as session:
        str_urls = []

        item = Item()
        item = item_handler.create_item(item, session)

        url_handler.prepare_and_store_urls(item, str_urls, session)
        for str_url in ["www.compact-online.de/utes-moma-2-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen-die-corona-regeln"]:
            verify_and_get_url(item, str_url, session)

        assert item.status != 'Unsafe'

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
