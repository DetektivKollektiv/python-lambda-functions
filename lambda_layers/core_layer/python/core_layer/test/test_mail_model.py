import pytest
from uuid import uuid4
from core_layer.db_handler import Session
from core_layer.model.mail_model import Mail
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.model.submission_model import Submission
from core_layer import helper


@pytest.fixture
def mail_id():
    return str(uuid4())

@pytest.fixture
def user_id():
    return str(uuid4())

@pytest.fixture
def submission_id():
    return str(uuid4())

@pytest.fixture
def mailaddress():
    return "a@b.c"

@pytest.fixture
def username():
    return "Michael Jackson"


def test_mail_model(mail_id, user_id, submission_id, mailaddress, username):

    with Session() as session:
              
        # Create User object
        user_obj = User(id = user_id, 
                        name = username)
        level_1_obj = Level(id = 1)

        # Create Mail object and check relationship to 'users' table 
        mail_obj = Mail(id = mail_id,
                        email = mailaddress,
                        user_id = user_id)

        # Create Submission object
        submission_obj = Submission(id = submission_id,
                                    mail_id = mail_id,
                                    submission_date = helper.get_date_time_now())
        session.add_all([user_obj, level_1_obj, mail_obj, submission_obj])
        session.commit()

        assert session.query(Mail).first().email == mailaddress # check: entry in mail model
        assert session.query(Mail).first().user.name == username # check: relationship to user model
        assert session.query(User).first().email.id == mail_id # check: reverse direction
        assert session.query(Mail).first().submissions[0].id == submission_id # check: relationship to submissions model
        assert session.query(Submission).first().mail.email == mailaddress # check: reverse direction