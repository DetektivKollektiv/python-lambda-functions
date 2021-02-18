from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func
import boto3
from datetime import date
from core_layer.connection_handler import get_db_session, update_object
from core_layer import helper

from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.model.review_model import Review


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
    user = session.query(User).filter(User.id == id).one()
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


def get_top_users(n, attr, descending, is_test, session) -> [User]:
    """
    Returns the top "n" users as sorted by "attr" in descending or ascending order as set by "descending". 

    Parameters
    ----------
    n: int, required
        the number of users to return
    attr: str, required
        the column on the users table to sort by
    descending: bool, required
        which order to sort the rows by column 'attr' in False = ASC or True =DESC
    is_test: bool, required
        is this code being run as part of the tests or in production
    session: Session??, required
        a database session
    Returns
    ------
    users: [User]
        A list including the top n user objects as ordered by attr, desc
    """
    session = get_db_session(is_test, session)
    sort_column = getattr(User, attr).desc() if descending else getattr(User, attr)
    users = session.query(User).order_by(sort_column).limit(n).all()
    return users

def get_all_users(is_test, session) -> [User]:
    """Returns a user by their id

    Parameters
    ----------

    Returns
    ------
    users: [User]
        A list including all user objects
    """

    session = get_db_session(is_test, session)
    users = session.query(User).all()
    return users


def get_user_progress(user: User, is_test, session) -> int:
    """Returns the users progress towards the next level

    Parameters
    ----------
    user: User, required
        The user for which to return progress

    Returns
    ------
    progress: int
        Progress cast to an int value (between 0 and 100)
    """
    current_level = session.query(Level).filter(
        Level.id == user.level_id).one()
    next_level = session.query(Level).filter(
        Level.id == user.level_id + 1).one()

    exp_difference = next_level.required_experience_points - \
        current_level.required_experience_points
    exp_in_current_level = user.experience_points - \
        current_level.required_experience_points

    progress = int(exp_in_current_level / exp_difference * 100)

    return progress


def get_needed_exp(user: User, is_test, session) -> int:
    """Returns how many exp are needed for the user to level up

    Parameters
    ----------
    user: User, required
        The user for which to return progress

    Returns
    ------
    exp: int
        The amount of exp needed to level up
    """
    next_level = session.query(Level).filter(
        Level.id == user.level_id + 1).one()

    exp_difference = next_level.required_experience_points - \
        user.experience_points

    return exp_difference


def get_user_rank(user: User, level_rank: bool, is_test, session: Session) -> int:
    """Returns the users rank.

    Parameters
    ----------
    user: User, required
        The user for which to return rank
    level_rank: bool, required
        Whether to limit the rank to users within the same level

    Returns
    ------
    rank: int
        The user's rank
    """

    closed_review_count = session.query(Review).filter(
        Review.status == 'closed', Review.user_id == user.id).count()

    if closed_review_count == 0:
        if level_rank:
            user_count = session.query(User).filter(
                User.level_id == user.level_id).count()
        else:
            user_count = session.query(User).count()

        return user_count
        # raise Exception("User has not created any reviews yet")
    if level_rank:
        count_subquery = session.query(
            User,
            func.count(User.id).label('closed_review_count')). \
            join(User.reviews). \
            filter(Review.status == "closed", User.level_id == user.level_id). \
            group_by(User.id). \
            order_by(func.count(User.id))

    else:
        count_subquery = session.query(
            User,
            func.count(User.id).label('closed_review_count')). \
            join(User.reviews). \
            filter(Review.status == "closed"). \
            group_by(User.id). \
            order_by(func.count(User.id).desc())
    i = 1
    for row in count_subquery.all():
        if row.User.id == user.id:
            return i
        i += 1

    raise Exception("Could not get rank for user")


def get_solved_cases(user: User, today: bool, is_test, session: Session) -> int:
    """Returns the amount of cases a user solved.

    Parameters
    ----------
    user: User, required
        The user for which to return the number of solved cases
    today: bool, required
        Whether to limit this function to today's cases

    Returns
    ------
    count: int
        The number of solved cases
    """

    if not today:
        count = session.query(Review).filter(
            Review.user_id == user.id,
            Review.status == "closed"
        ).count()
    else:
        count = session.query(Review).filter(
            Review.user_id == user.id,
            func.date(Review.finish_timestamp) == date.today(),
            Review.status == "closed"
        ).count()

    return count
