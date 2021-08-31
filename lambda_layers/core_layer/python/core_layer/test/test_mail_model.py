import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from core_layer.model.mail_model import Mail



@pytest.fixture
def mail_id():
    return str(uuid4())


def test_mail_model(mail_id):

    with Session() as session:

        mail_obj = Mail(id = mail_id)
        session.add(mail_obj)
        session.commit()

        assert session.query(Mail).first().id == mail_id