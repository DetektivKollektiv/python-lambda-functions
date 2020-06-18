from uuid import uuid4
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine
from crud.model import Item


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

    db = create_engine('mysql+auroradataapi://:@/development_db',
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
