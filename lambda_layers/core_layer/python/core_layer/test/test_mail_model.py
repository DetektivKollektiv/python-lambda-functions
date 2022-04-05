import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from core_layer.model.mail_model import Mail
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.model.submission_model import Submission
from datetime import datetime


@pytest.fixture
def mail_id():
    return str(uuid4())

@pytest.fixture
def user_ids():
    return [str(uuid4()), str(uuid4())]

@pytest.fixture
def submission_id():
    return str(uuid4())

@pytest.fixture
def mailaddress():
    return "a@b.c"

@pytest.fixture
def usernames():
    return ["Michael Jackson", "Janet Jackson"]


def test_mail_model(mail_id, user_ids, submission_id, mailaddress, usernames):

    with Session() as session:
              
        level_1_obj = Level(id = 1)

        mail_obj = Mail(id = mail_id,
                        email = mailaddress)

        user1_obj = User(id = user_ids[0], 
                         name = usernames[0],
                         mail_id = mail_id)       

        user2_obj = User(id = user_ids[1],
                         name = usernames[1],
                         mail_id = mail_id)

        submission_obj = Submission(id = submission_id,
                                    mail_id = mail_id,
                                    submission_date = datetime.now())

        session.add_all([level_1_obj, mail_obj, user1_obj, user2_obj, submission_obj])
        session.commit()

        assert session.query(Mail).first().email == mailaddress # check: entry in mail model
        for i in range(2): # check: 2 users with same mail address
            assert session.query(Mail).first().users[i].id == user_ids[i]
            assert session.query(Mail).first().users[i].name == usernames[i] 
            assert session.query(Mail).first().users[i].mail.email == mailaddress
            assert session.query(User).all()[i].mail.email == mailaddress
        assert session.query(Mail).first().submissions[0].id == submission_id # check: relationship to submissions model
        assert session.query(Submission).first().mail.email == mailaddress # check: reverse direction