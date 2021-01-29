import pytest
from core_layer.model import Submission
from uuid import uuid4
from sqlalchemy import func
from datetime import timedelta, datetime
from submission_service.anonymize_unconfimed_submissions import anonymize_unconfirmed_submissions
from core_layer.connection_handler import get_db_session
from core_layer import helper


@pytest.fixture
def submission1():
    three_days_ago = helper.get_date_time(
        datetime.now() - timedelta(days=3), True)

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


@pytest.fixture
def session(submission1, submission2):
    session = get_db_session(True, None)
    session.add(submission1)
    session.add(submission2)
    session.commit()
    return session


def test_mail_anonymization(session):
    submissions = session.query(Submission).filter(
        Submission.mail == None).all()
    assert len(submissions) == 0
    anonymize_unconfirmed_submissions(None, None, True, session)
    submissions = session.query(Submission).filter(
        Submission.mail == None).all()
    assert len(submissions) == 1
