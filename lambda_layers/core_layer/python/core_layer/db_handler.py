import logging
import sqlite3
import os
from this import d

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql.expression import case
from .model.model_base import Base

"""Initializes a Database Session."""

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('New DB Session initiated')

cluster_arn = "arn:aws:rds:eu-central-1:891514678401:cluster:serverless-db"
secret_arn = "arn:aws:secretsmanager:eu-central-1:891514678401:secret:ServerlessDBSecret-7oczW5"

if 'DBNAME' in os.environ:
    database_name = os.environ['DBNAME']
    db = create_engine('mysql+auroradataapi://:@/{0}'.format(database_name),
                       echo=True,
                       connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))
else:
    def creator(): return sqlite3.connect(
        'file::memory:?cache=shared', uri=True, check_same_thread=False)
    db = create_engine('sqlite://', creator=creator)

    Base.metadata.create_all(db)
    db.execute('pragma foreign_keys=on')


session_factory = sessionmaker(bind=db, expire_on_commit=False, autoflush=True)
Session = scoped_session(session_factory)


def update_object(obj, session):
    """Updates an existing item in the database.

    Parameters
    ----------
    obj: object to be merged in the DB, required

    Returns
    ------
    obj: The merged object
    """
    try:
        session.merge(obj)
        session.commit()
        return obj
    except Exception:
        logging.exception('Could not update object.')
        session.rollback()
        return None


def add_object(obj, session):
    """Adds an existing item to the database.

    Parameters
    ----------
    obj: object to be stored, required

    Returns
    ------
    obj: The stored object
    """
    try:
        session.add(obj)
        session.commit()
        return obj
    except Exception:
        logging.exception('Could not store object.')
        session.rollback()
        return None

def init_database():
    Base.metadata.create_all(db)

def clear_database():
    Base.metadata.drop_all(db)