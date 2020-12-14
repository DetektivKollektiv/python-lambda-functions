# External imports
from uuid import uuid4
from sqlalchemy.orm import Session
# Helper imports
from core_layer.connection_handler import get_db_session
from core_layer import helper
# Model imports
from core_layer.model.submission_model import Submission


def create_submission_db(submission, is_test, session):
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
    session = get_db_session(is_test, session)

    submission.id = str(uuid4())
    submission.submission_date = helper.get_date_time_now(is_test)

    session.add(submission)
    session.commit()

    return submission


def get_submissions_by_item_id(item_id, is_test, session):

    session = get_db_session(is_test, session)
    submissions = session.query(Submission).filter(
        Submission.item_id == item_id).all()
    return submissions
