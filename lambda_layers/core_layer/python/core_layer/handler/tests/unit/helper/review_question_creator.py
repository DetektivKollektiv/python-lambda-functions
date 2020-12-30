from core_layer.model import ReviewQuestion


def create_review_question(question_id, item_type_id, max_children=0):
    review_question = ReviewQuestion()

    review_question.id = question_id
    review_question.item_type_id = item_type_id
    review_question.max_children = max_children

    return review_question
