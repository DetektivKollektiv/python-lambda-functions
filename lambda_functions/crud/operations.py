import os
from uuid import uuid4
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine
from crud.model import Item, Submission
from datetime import datetime


def get_db_session():
    """Returns a DB session

    Returns
    ------
    db: DB Connection
        The database connection
    """

    # TODO Environment variables, put db session in seperate class
    cluster_arn = "arn:aws:rds:eu-central-1:891514678401:cluster:serverless-db"
    secret_arn = "arn:aws:secretsmanager:eu-central-1:891514678401:secret:ServerlessDBSecret-7oczW5"

    database_name = os.environ['DBNAME']

    db = create_engine('mysql+auroradataapi://:@/{0}'.format(database_name),
                       echo=True,
                       connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))

    Session = sessionmaker(bind=db)
    session = Session()

    return session


def create_item_db(item):
    """Inserts a new item into the database

    Parameters
    ----------
    item: Item, required
        The item to be inserted

    Returns
    ------
    item: Item
        The inserted item
    """

    session = get_db_session()

    item.id = str(uuid4())
    item.status = "new"
    session.add(item)
    session.commit()

    return item


def get_all_items_db():
    """Returns all items from the database

    Returns
    ------
    items: Item[]
        The items
    """

    session = get_db_session()
    items = session.query(Item).all()
    return items


def get_item_by_content_db(content):
    """Returns an item with the specified content from the database

        Returns
        ------
        item: Item
            The item
        Null, if no item was found
        """
    session = get_db_session()
    item = session.query(Item).filter(Item.content == content).first()
    if item is None:
        raise Exception("No item found.")
    return item


def create_submission_db(submission):
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
    session = get_db_session()

    submission.id = str(uuid4())
    submission.submission_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    session.add(submission)
    session.commit()

    return submission


def get_all_submissions_db():

    session = get_db_session()
    submissions = session.query(Submission).all()
    return submissions
