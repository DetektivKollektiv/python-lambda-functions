from crud import operations
from crud.model import ReviewAnswer
from review_answer_handler import create_review_answer
from . import event_creator

import json

def test_create_review_answer(monkeypatch):
    """
    Creates a simple ReviewAnswer without any further steps necessarry
    """

    monkeypatch.setenv("DBNAME", "Test")    
    session = operations.get_db_session(True, None)

    review_answer = ReviewAnswer()
    
    # TODO: Check why guids and ints are wiredly written into object
    review_answer.id = '1',
    review_answer.review_id = '2',
    review_answer.review_question_id = '3',
    review_answer.answer = 5,
    review_answer.comment = 'Test Review Answer'

    event = event_creator.get_create_review_answer_event(review_answer)

    resp = create_review_answer(event, None, True, session)

    print(resp)    
    
    body = json.loads(resp["body"])

    assert body["id"] != review_answer.id
    assert body["review_id"] == review_answer.review_id
    assert body["review_question_id"] == review_answer.review_question_id
    assert body["answer"] == review_answer.answer
    assert body["comment"] == review_answer.comment