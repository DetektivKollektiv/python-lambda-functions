# External imports
from uuid import uuid4
from datetime import timedelta, datetime
# Helper imports
from core_layer import helper
# Model imports
from core_layer.model.submission_model import Submission


def create_submission_db(submission, session):
    """Inserts a new submission into the database

    Parameters
    ----------
    submission: Submission, required
        The submission to be inserted

    Returns
    ------
    submission: Submission
        The inserted submission
    """

    submission.id = str(uuid4())
    submission.submission_date = helper.get_date_time_now()

    session.add(submission)
    session.commit()

    return submission


def get_submissions_by_item_id(item_id, session):

    submissions = session.query(Submission).filter(
        Submission.item_id == item_id).all()
    return submissions


def confirm_submission(submission_id, session):

    submission = session.query(Submission).filter(
        Submission.id == submission_id).one()
    submission.status = 'confirmed'
    session.merge(submission)
    session.commit()
    return submission


def anonymize_unconfirmed_submissions(session):

    two_days_ago = helper.get_date_time(datetime.now() - timedelta(days=2))
    submissions = session.query(Submission).filter(
        Submission.status == 'unconfirmed', Submission.submission_date < two_days_ago).all()
    counter = 0
    for submission in submissions:
        submission.mail = None
        session.merge(submission)
        counter += 1

    session.commit()
    return counter
