from core_layer.model.user_model import User
from core_layer.model.item_model import Item
from core_layer.model.level_model import Level
from core_layer.model.review_question_model import ReviewQuestion
from core_layer.handler import user_handler

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, Session, sessionmaker
from ..helper import event_creator

# TODO: extract functions to create entities (e.g. create_level) - maybe move them to separate file


def create_level(id: int, desc: str, req_exp: int) -> Level:
    """
    Creates a level object
    """
    level = Level()
    level.id = id
    level.description = desc
    level.required_experience_points = req_exp

    return level


def create_users_for_ranking(session) -> Session:
    """ 
    Creates My Detective looking up ranking and his own position
    3 different Levels (Junior, Senior, Master)
    20 Users on Junior Level, 20 Users on Senior Level, 20 Users on Master Level
    """
    my_detective = User()
    my_detective.id = "999"
    my_detective.name = "MyDetektiv"
    user_handler.create_user(my_detective, True, session)
    my_detective.level_id = 2
    my_detective.experience_points = 35
    my_detective.sign_up_timestamp = datetime.today()
    
    levels_to_create = [
        { 'id': 1, 'description': 'Junior', 'required_experience_points': 0 },
        { 'id': 2, 'description': 'Senior', 'required_experience_points': 20 },
        { 'id': 3, 'description': 'Master', 'required_experience_points': 40 }
    ]
    
    level1_id = levels_to_create[0]['id']
    level2_id = levels_to_create[1]['id']
    level3_id = levels_to_create[2]['id']

    for level in levels_to_create:
        new_level = session.query(Level).get(level['id'])
        if new_level is None:
            new_level = create_level(level['id'], level['description'], level['required_experience_points'])
            session.add(new_level)

    users_to_create = []

    # the last created will be 60
    for i in range(1, 21):
        users_to_create.append({
            'id': str(i),
            'name': "JuniorUser" + str(i),
            'level_id': level1_id,
            'experience_points': i,
            'sign_up_timestamp': datetime.today() - timedelta(days=i)
        })
    for i in range(21, 41):
        users_to_create.append({
            'id': str(i),
            'name': "SeniorUser" + str(i),
            'level_id': level2_id,
            'experience_points': i,
            'sign_up_timestamp': datetime.today() - timedelta(days=i)
        })
    for i in range(41, 61):
        users_to_create.append({
            'id': str(i),
            'name': "MasterUser" + str(i),
            'level_id': level3_id,
            'experience_points': i,
            'sign_up_timestamp': datetime.now() - timedelta(days=i)
        })
    
    
    for new_user in users_to_create:
        user_already_exists = session.query(User).get(new_user['id']) is not None
        # todo -> should wipe the database before the tests, instead of allowing tests to share the same data
        if(not user_already_exists):
            user = User()
            user.id = str(new_user['id'])
            user = user_handler.create_user( user, True, session)
            user.name = new_user['name']
            user.level_id = new_user['level_id']
            user.experience_points = new_user['experience_points']
            user.sign_up_timestamp = new_user['sign_up_timestamp']
            session.merge(user)

    session.commit()
    
    return session


def create_levels_junior_and_senior_detectives(session):
    """
    This method can be used to setup a testing scenario.
    It adds the following objects to a session:
    - 3 levels requiring 0, 5 and 10 experience points
    - 4 detectives with level 1 and ids 1 - 4
    - 4 detectives with level 2 and ids 11 - 14
    """

    # Create three levels
    level1 = create_level(1, "Junior", 0)
    level2 = create_level(2, "Senior", 5)
    level3 = create_level(3, "master", 10)

    session.add(level1)
    session.add(level2)
    session.add(level3)

    # Create 4 level-1-detectives
    junior_detective1 = User()
    junior_detective1.id = "1"
    junior_detective1.name = "Junior1"
    user_handler.create_user(junior_detective1, True, session)

    junior_detective2 = User()
    junior_detective2.id = "2"
    junior_detective2.name = "Junior2"
    user_handler.create_user(junior_detective2, True, session)

    junior_detective3 = User()
    junior_detective3.id = "3"
    junior_detective3.name = "Junior3"
    user_handler.create_user(junior_detective3, True, session)

    junior_detective4 = User()
    junior_detective4.id = "4"
    junior_detective4.name = "Junior4"
    user_handler.create_user(junior_detective4, True, session)

    junior_detective5 = User()
    junior_detective5.id = "5"
    junior_detective5.name = "Junior5"
    user_handler.create_user(junior_detective5, True, session)

    # Create 4 level-2-detectives
    senior_detective1 = User()
    senior_detective1.id = "11"
    senior_detective1.name = "Senior1"
    senior_detective1 = user_handler.create_user(
        senior_detective1, True, session)
    senior_detective1.level_id = 2
    senior_detective1.experience_points = 5

    senior_detective2 = User()
    senior_detective2.id = "12"
    senior_detective2.name = "Senior2"
    senior_detective2 = user_handler.create_user(
        senior_detective2, True, session)
    senior_detective2.level_id = 2
    senior_detective2.experience_points = 5

    senior_detective3 = User()
    senior_detective3.id = "13"
    senior_detective3.name = "Senior3"
    senior_detective3 = user_handler.create_user(
        senior_detective3, True, session)
    senior_detective3.level_id = 2
    senior_detective3.experience_points = 5

    senior_detective4 = User()
    senior_detective4.id = "14"
    senior_detective4.name = "Senior4"
    senior_detective4 = user_handler.create_user(
        senior_detective4, True, session)
    senior_detective4.level_id = 2
    senior_detective4.experience_points = 5

    senior_detective5 = User()
    senior_detective5.id = "15"
    senior_detective5.name = "Senior5"
    senior_detective5 = user_handler.create_user(
        senior_detective5, True, session)
    senior_detective5.level_id = 2
    senior_detective5.experience_points = 5

    session.merge(senior_detective1)
    session.merge(senior_detective2)
    session.merge(senior_detective3)
    session.merge(senior_detective4)
    session.merge(senior_detective5)
    session.commit()

    return session


def create_questions(session):

    parentquestion1 = ReviewQuestion()
    parentquestion1.id = "1"
    parentquestion1.info = "1"
    parentquestion1.max_children = 2

    childquestion1a = ReviewQuestion()
    childquestion1a.id = "1a"
    childquestion1a.content = "1a"
    childquestion1a.parent_question_id = "1"
    childquestion1a.upper_bound = 4
    childquestion1a.lower_bound = 3

    childquestion1b = ReviewQuestion()
    childquestion1b.id = "1b"
    childquestion1b.content = "1b"
    childquestion1b.parent_question_id = "1"
    childquestion1b.upper_bound = 2
    childquestion1b.lower_bound = 1

    childquestion1c = ReviewQuestion()
    childquestion1c.id = "1c"
    childquestion1c.content = "1c"
    childquestion1c.parent_question_id = "1"
    childquestion1c.upper_bound = 3
    childquestion1c.lower_bound = 2

    parentquestion2 = ReviewQuestion()
    parentquestion2.id = "2"
    parentquestion2.info = "2"
    parentquestion2.max_children = 1

    childquestion2a = ReviewQuestion()
    childquestion2a.id = "2a"
    childquestion2a.content = "2a"
    childquestion2a.parent_question_id = "2"
    childquestion2a.upper_bound = 4
    childquestion2a.lower_bound = 3

    childquestion2b = ReviewQuestion()
    childquestion2b.id = "2b"
    childquestion2b.content = "2b"
    childquestion2b.parent_question_id = "2"
    childquestion2b.upper_bound = 2
    childquestion2b.lower_bound = 1

    parentquestion3 = ReviewQuestion()
    parentquestion3.id = "3"
    parentquestion3.info = "3"
    parentquestion3.max_children = None

    parentquestion4 = ReviewQuestion()
    parentquestion4.id = "4"
    parentquestion4.info = "4"
    parentquestion4.max_children = None

    parentquestion5 = ReviewQuestion()
    parentquestion5.id = "5"
    parentquestion5.info = "5"
    parentquestion5.max_children = None

    parentquestion6 = ReviewQuestion()
    parentquestion6.id = "6"
    parentquestion6.info = "6"
    parentquestion6.max_children = None

    parentquestion7 = ReviewQuestion()
    parentquestion7.id = "7"
    parentquestion7.info = "7"
    parentquestion7.max_children = None

    parentquestion8 = ReviewQuestion()
    parentquestion8.id = "8"
    parentquestion8.info = "8"
    parentquestion8.max_children = None

    parentquestion9 = ReviewQuestion()
    parentquestion9.id = "9"
    parentquestion9.info = "9"
    parentquestion9.max_children = None

    parentquestion10 = ReviewQuestion()
    parentquestion10.id = "10"
    parentquestion10.info = "10"
    parentquestion10.max_children = None

    session.add(parentquestion1)
    session.add(parentquestion2)
    session.add(parentquestion3)
    session.add(parentquestion4)
    session.add(parentquestion5)
    session.add(parentquestion6)
    session.add(parentquestion7)
    session.add(parentquestion8)
    session.add(parentquestion9)
    session.add(parentquestion10)
    session.add(childquestion1a)
    session.add(childquestion1b)
    session.add(childquestion1c)
    session.add(childquestion2a)
    session.add(childquestion2b)
    session.commit()

    return session
