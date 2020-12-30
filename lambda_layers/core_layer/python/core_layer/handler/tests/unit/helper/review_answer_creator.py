from core_layer.model.review_answer_model import ReviewAnswer


def generate_answer(answer, review_id=None, review_question_id=None) -> ReviewAnswer:
    review_answer = ReviewAnswer()
    review_answer.answer = answer
    review_answer.review_id = review_id
    review_answer.review_question_id = review_question_id

    return review_answer
