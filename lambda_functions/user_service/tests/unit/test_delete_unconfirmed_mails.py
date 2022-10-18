import pytest
from core_layer.model import Mail
from uuid import uuid4
from sqlalchemy import func
from datetime import timedelta, datetime
from core_layer.db_handler import Session
from user_service.delete_unconfirmed_mails import delete_unconfirmed_mails


@pytest.fixture
def mail1():
    three_days_ago = datetime.now() - timedelta(days=3)

    mail = Mail()
    mail.id = str(uuid4())
    mail.email = "Test_three_days_ago@test.de"
    mail.timestamp = three_days_ago
    mail.status = "unconfirmed"
    return mail

@pytest.fixture
def mail2():
    mail = Mail()
    mail.id = str(uuid4())
    mail.email = "Test_now@test.de"
    mail.timestamp = func.now()
    mail.status = "unconfirmed"
    return mail


def test_delete_unconfirmed_mails(mail1, mail2):

    with Session() as session:

        session.add(mail1)
        session.add(mail2)
        session.commit()

        # check number of mails before deletion
        mails = session.query(Mail).filter(
            Mail.status == "unconfirmed").all()
        assert len(mails) == 2

        # delete unconfirmed mails
        delete_unconfirmed_mails(event = "", context = "")
        # check number of mails after deletion and verify 1 of 2 has been deleted
        mails = session.query(Mail).filter(
            Mail.status == "unconfirmed").all()
        assert len(mails) == 1 # only 1 of 2 ist left
        assert mails[0].email == "Test_now@test.de" # the older one was deleted