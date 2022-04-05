import pytest
from core_layer.model import Submission
from uuid import uuid4
from sqlalchemy import func
from datetime import timedelta, datetime
from submission_service.anonymize_unconfirmed_submissions import anonymize_unconfirmed_submissions
from core_layer.db_handler import Session
from core_layer import helper


@pytest.fixture
def submission1():
    three_days_ago = datetime.now() - timedelta(days=3)

    submission = Submission()
    submission.id = str(uuid4())
    submission.mail = "Test@test.de"
    submission.submission_date = three_days_ago
    return submission


@pytest.fixture
def submission2():
    submission = Submission()
    submission.id = str(uuid4())
    submission.mail = "Test@test.de"
    submission.submission_date = func.now()
    return submission


def test_mail_anonymization(submission1, submission2):

    with Session() as session:

        session.add(submission1)
        session.add(submission2)
        session.commit()

        submissions = session.query(Submission).filter(
            Submission.mail == None).all()
        assert len(submissions) == 0
        anonymize_unconfirmed_submissions(None, None)
        submissions = session.query(Submission).filter(
            Submission.mail == None).all()
        assert len(submissions) == 1
