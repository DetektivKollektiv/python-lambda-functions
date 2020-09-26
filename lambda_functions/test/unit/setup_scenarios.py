import crud.operations as operations
from crud.model import User, Item, Level
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
import test.unit.event_creator as event_creator


def create_levels_junior_and_senior_detectives(session):
    """
    This method can be used to setup a testing scenario.
    It adds the following objects to a session:
    - 3 levels requiring 0, 5 and 10 experience points
    - 4 detectives with level 1 and ids 1 - 4
    - 4 detectives with level 2 and ids 11 - 14
    """

    # Create three levels
    level1 = Level()
    level1.id = 1
    level1.description = "Junior"
    level1.required_experience_points = 0

    level2 = Level()
    level2.id = 2
    level2.description = "Senior"
    level2.required_experience_points = 5

    level3 = Level()
    level3.id = 3
    level3.description = "master"
    level3.required_experience_points = 10

    session.add(level1)
    session.add(level2)
    session.add(level3)

    # Create 4 level-1-detectives
    junior_detective1 = User()
    junior_detective1.id = "1"
    junior_detective1.name = "Junior1"
    operations.create_user_db(junior_detective1, True, session)

    junior_detective2 = User()
    junior_detective2.id = "2"
    junior_detective2.name = "Junior2"
    operations.create_user_db(junior_detective2, True, session)

    junior_detective3 = User()
    junior_detective3.id = "3"
    junior_detective3.name = "Junior3"
    operations.create_user_db(junior_detective3, True, session)

    junior_detective4 = User()
    junior_detective4.id = "4"
    junior_detective4.name = "Junior4"
    operations.create_user_db(junior_detective4, True, session)

    # Create 4 level-2-detectives
    senior_detective1 = User()
    senior_detective1.id = "11"
    senior_detective1.name = "Senior1"
    senior_detective1 = operations.create_user_db(
        senior_detective1, True, session)
    senior_detective1.level_id = 2
    senior_detective1.experience_points = 5

    senior_detective2 = User()
    senior_detective2.id = "12"
    senior_detective2.name = "Senior2"
    senior_detective2 = operations.create_user_db(
        senior_detective2, True, session)
    senior_detective2.level_id = 2
    senior_detective2.experience_points = 5

    senior_detective3 = User()
    senior_detective3.id = "13"
    senior_detective3.name = "Senior3"
    senior_detective3 = operations.create_user_db(
        senior_detective3, True, session)
    senior_detective3.level_id = 2
    senior_detective3.experience_points = 5

    senior_detective4 = User()
    senior_detective4.id = "14"
    senior_detective4.name = "Senior4"
    senior_detective4 = operations.create_user_db(
        senior_detective4, True, session)
    senior_detective4.level_id = 2
    senior_detective4.experience_points = 5

    session.merge(senior_detective1)
    session.merge(senior_detective2)
    session.merge(senior_detective3)
    session.merge(senior_detective4)
    session.commit()

    return session
