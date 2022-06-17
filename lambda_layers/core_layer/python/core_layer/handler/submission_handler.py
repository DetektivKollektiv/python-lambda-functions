# External imports
from uuid import uuid4
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

    session.add(submission)
    session.commit()

    return submission


def get_submissions_by_item_id(item_id, session):

    submissions = session.query(Submission).filter(
        Submission.item_id == item_id).all()
    return submissions