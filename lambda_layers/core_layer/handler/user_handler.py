from uuid import uuid4
from sqlalchemy.orm import Session
import boto3
from core_layer.connection_handler import get_db_session, update_object
from core_layer import helper

from core_layer.model.user_model import User
from core_layer.model.level_model import Level


def get_user_by_id(id, is_test, session):
    """Returns a user by their id

    Parameters
    ----------
    id: str, required
        The id of the user

    Returns
    ------
    user: User
        The user
    """

    session = get_db_session(is_test, session)
    user = session.query(User).get(id)
    return user


def delete_user(event, is_test, session):
    """Deletes a user from the database.

    Parameters
    ----------
    user_id: str, required
             The id of the user

    Returns
    ------
    nothing
    """
    if session is None:
        session = get_db_session(is_test, session)

    user_id = helper.cognito_id_from_event(event)
    user = session.query(User).get(user_id)

    if(user == None):
        raise Exception(
            f"User with id {user_id} could not be found in database.")

    client = boto3.client('cognito-idp')
    client.admin_delete_user(
        UserPoolId=event['requestContext']['identity']['cognitoAuthenticationProvider'].split(',')[
            0].split('amazonaws.com/')[1],
        Username=user.name
    )

    session.delete(user)
    session.commit()


def create_user(user, is_test, session):
    """Inserts a new user into the database

    Parameters
    ----------
    user: User, required
        The user to be inserted

    Returns
    ------
    user: User
        The inserted user
    """
    if session == None:
        session = get_db_session(is_test, session)

    user.score = 0
    user.level_id = 1
    user.experience_points = 0
    session.add(user)
    session.commit()

    return user


def give_experience_point(user_id, is_test, session):
    user = get_user_by_id(user_id, is_test, session)
    user.experience_points = user.experience_points + 1
    new_level = session.query(Level) \
        .filter(Level.required_experience_points <= user.experience_points) \
        .order_by(Level.required_experience_points.desc()) \
        .first()

    if new_level != user.level_id:
        user.level_id = new_level.id
    update_object(user, is_test, session)
