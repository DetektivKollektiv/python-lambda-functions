from core_layer.db_handler import Session

from core_layer.model.review_question_model import ReviewQuestion
from core_layer.model.review_answer_model import AnswerOption

from core_layer.test.helper.fixtures import database_fixture

def test_questions_and_answers(database_fixture):
    with Session() as session:

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
