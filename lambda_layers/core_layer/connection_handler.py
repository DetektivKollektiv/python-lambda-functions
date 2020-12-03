import logging
import sqlite3
import os

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session, sessionmaker
from model_base import Base


def get_db_session(is_test, session) -> Session:
    """Returns a DB session

    Returns
    ------
    db: DB Connection
        The database connection
    """

    # put db session in seperate class

    if session != None:
        return session

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info('New DB Session initiated')

    cluster_arn = "arn:aws:rds:eu-central-1:891514678401:cluster:serverless-db"
    secret_arn = "arn:aws:secretsmanager:eu-central-1:891514678401:secret:ServerlessDBSecret-7oczW5"

    if is_test == False:
        database_name = os.environ['DBNAME']
        db = create_engine('mysql+auroradataapi://:@/{0}'.format(database_name),
                           echo=True,
                           connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))
    else:
        def creator(): return sqlite3.connect(
            'file::memory:?cache=shared', uri=True, check_same_thread=False)
        db = create_engine('sqlite://', creator=creator)
        Base.metadata.create_all(db)

    Session = sessionmaker(bind=db, expire_on_commit=False)
    session = Session()

    return session


def update_object(obj, is_test, session):
    """Updates an existing item in the database

    Parameters
    ----------
    obj: object to be merged in the DB, required
        The item to be updates

    Returns
    ------
    obj: The merged object
    """
    session = get_db_session(is_test, session)

    session.merge(obj)
    session.commit()
    return obj
