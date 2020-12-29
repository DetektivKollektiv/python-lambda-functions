from core_layer.model import ReviewQuestion


def create_review_question(question_id, item_type_id):
  review_question = ReviewQuestion()

  review_question.id = question_id
  review_question.item_type_id = item_type_id

  return review_question
