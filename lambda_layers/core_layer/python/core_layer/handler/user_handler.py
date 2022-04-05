from core_layer.db_handler import update_object
from sqlalchemy import func
import boto3
from typing import List
from datetime import date, datetime, timedelta
from core_layer import helper

from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from core_layer.model.review_model import Review


def get_user_by_id(id, session):
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

    user = session.query(User).filter(User.id == id).one()
    return user


def delete_user(event, session):
    """Deletes a user from the database.

    Parameters
    ----------
    user_id: str, required
             The id of the user

    Returns
    ------
    nothing
    """

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


def create_user(user, session):
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

    session.add(user)
    session.commit()

    return user


def give_experience_point(user_id, session):
    user = get_user_by_id(user_id, session)
    user.experience_points = user.experience_points + 1
    new_level = session.query(Level) \
        .filter(Level.required_experience_points <= user.experience_points) \
        .order_by(Level.required_experience_points.desc()) \
        .first()

    if new_level.id != user.level_id:
        user.level_id = new_level.id
    update_object(user, session)


def get_top_users(n, attr, descending, session) -> List[User]:
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
    session: Session??, required
        a database session
    Returns
    ------
    users: [User]
        A list including the top n user objects as ordered by attr, desc
    """

    sort_column = getattr(User, attr).desc(
    ) if descending else getattr(User, attr)

    users = session.query(User).order_by(sort_column).limit(n).all()
    return users


def get_top_users_by_period(n, p, attr, descending, session) -> List[User]:
    """
    Returns the top "n" users in a period (1 week)
    sorted by "attr" in descending or ascending order as set by "descending"

    Parameters
    ----------
    n: int, required
        the number of users to return
    p: period weeks, required

    attr: str, required
        the column on the users table to sort by
    descending: bool, required
        which order to sort the rows by column 'attr' in False = ASC or True =DESC
    session: Session??, required
        a database session
    Returns
    ------
    users: [User]
        A list including the top n user objects as ordered by attr, desc
    """

    compare_timestamp = datetime.now() - timedelta(weeks=p)
    sort_column = getattr(User, attr).desc(
    ) if descending else getattr(User, attr)

    users = session.query(User) \
        .filter(User.sign_up_timestamp >= compare_timestamp) \
        .order_by(sort_column) \
        .limit(n).all()
    return users


def get_top_users_by_level(user_level, n, attr, descending, session) -> List[User]:
    """
    Returns the top "n" users on the user's level
    sorted by "attr" in descending or ascending order as set by "descending"

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format
    n: int, required
        the number of users to return
    attr: str, required
        the column on the users table to sort by
    descending: bool, required
        which order to sort the rows by column 'attr' in False = ASC or True =DESC
    session: Session??, required
        a database session
    Returns
    ------
    users: [User]
        A list including the top n user objects as ordered by attr, desc
    """

    sort_column = getattr(User, attr).desc(
    ) if descending else getattr(User, attr)

    users = session.query(User) \
        .filter(User.level_id == user_level) \
        .order_by(sort_column) \
        .limit(n).all()
    return users


def get_all_users(session) -> List[User]:
    """Returns a user by their id

    Parameters
    ----------

    Returns
    ------
    users: [User]
        A list including all user objects
    """

    users = session.query(User).all()
    return users


def get_user_progress(user: User, session) -> int:
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


def get_needed_exp(user: User, session) -> int:
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


def get_user_rank(user: User, level_rank: bool, session) -> int:
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
    if level_rank:
        count_subquery = session.query(
            User,
            func.count(User.id).label('closed_review_count')). \
            join(User.reviews). \
            filter(Review.status == "closed", User.level_id == user.level_id). \
            group_by(User.id). \
            order_by(func.count(User.id).desc(), User.name)

    else:
        count_subquery = session.query(
            User,
            func.count(User.id).label('closed_review_count')). \
            join(User.reviews). \
            filter(Review.status == "closed"). \
            group_by(User.id). \
            order_by(func.count(User.id).desc(), User.name)
    i = 1
    for row in count_subquery.all():
        if row.User.id == user.id:
            return i
        i += 1

    raise Exception("Could not get rank for user")


def get_solved_cases(user: User, today: bool, session) -> int:
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
