from crud.model import ReviewAnswer

def generate_answer(answer) -> ReviewAnswer:
    review_answer = ReviewAnswer()
    review_answer.answer = answer

    return review_answer