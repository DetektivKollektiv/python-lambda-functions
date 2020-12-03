import crud.operations as operations
from crud.model import ReviewQuestion, AnswerOption, Item, User
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import session, relationship, backref, sessionmaker
import test.unit.event_creator as event_creator
import test.unit.setup_scenarios as scenarios
import json


def test_questions_and_answers(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app
    session = operations.get_db_session(True, None)

    q1 = ReviewQuestion()
    q1.id = "1"
    q1.content = "Es ist eine Quelle angegeben."

    q2 = ReviewQuestion()
    q2.id = "2"
    q2.content = "Die Rechtschreibung ist korrekt."

    o1 = AnswerOption()
    o1.id = "1"
    o1.text = "Stimme zu"
    o1.value = 4

    q1.options = [o1]

    assert len(q1.options) == 1
    assert len(o1.questions) == 1

    q2.options = [o1]

    assert len(q1.options) == 1
    assert len(o1.questions) == 2

    session.add(q1)
    session.add(q2)
    session.add(o1)
    options = session.query(AnswerOption).all()
    assert len(options) == 1
