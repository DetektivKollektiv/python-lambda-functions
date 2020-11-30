from core_layer.model import Submission
from sqlalchemy.orm import Session
from core_layer.connection_handler import get_db_session
from core_layer import helper
from uuid import uuid4


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
