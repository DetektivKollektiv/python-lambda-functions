from typing import List
from core_layer.model.review_model import Review


def get_create_review_answer_event(review_answer):

    event = {
        "body": {
            "id": review_answer.id,
            "review_id": review_answer.review_id,
            "review_question_id": review_answer.review_question_id,
            "answer": review_answer.answer,
            "comment": review_answer.comment
        }
    }

    return event


def get_create_review_event(user_id, item_id):

    accept_event = {
        "requestContext": {
            "identity": {
                "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(user_id)
            }
        },
        "body": {
            'item_id': item_id
        }
    }
    return accept_event


def get_get_review_event(user_id, review_id):

    accept_event = {
        "pathParameters": {
            "review_id": review_id
        },
        "requestContext": {
            "identity": {
                "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(user_id)
            }
        }
    }
    return accept_event


def get_next_question_event(review_id, previous_question_id=None):
    if previous_question_id == None:
        event = {
            "queryStringParameters": {
                "review_id": review_id
            }
        }
    else:
        event = {
            "queryStringParameters": {
                "review_id": review_id,
                "previous_question_id": previous_question_id
            }
        }

    return event


def get_review_event(review: Review, item_id, status, user_id, score, comment="Test comment", tags: List[str] = []):

    questions = []
    for answer in review.review_answers:
        if answer.review_question.parent_question_id is None:
            answer_dict = {
                "answer_id": answer.id,
                "question_id": answer.review_question_id,
                "content": answer.review_question.content,
                "info": answer.review_question.info,
                "hint": answer.review_question.hint,
                "lower_bound": answer.review_question.lower_bound,
                "upper_bound": answer.review_question.upper_bound,
                "parent_question_id": answer.review_question.parent_question_id,
                "max_children": answer.review_question.max_children,
                "answer_value": score,
                "comment": answer.comment,
            }
            questions.append(answer_dict)
        else:
            if answer.review_question.lower_bound > score or answer.review_question.upper_bound < score:
                answer_dict = {
                    "answer_id": answer.id,
                    "question_id": answer.review_question_id,
                    "content": answer.review_question.content,
                    "info": answer.review_question.info,
                    "hint": answer.review_question.hint,
                    "lower_bound": answer.review_question.lower_bound,
                    "upper_bound": answer.review_question.upper_bound,
                    "parent_question_id": answer.review_question.parent_question_id,
                    "max_children": answer.review_question.max_children,
                    "answer_value": None,
                    "comment": answer.comment,
                }
            else:
                answer_dict = {
                    "answer_id": answer.id,
                    "question_id": answer.review_question_id,
                    "content": answer.review_question.content,
                    "info": answer.review_question.info,
                    "hint": answer.review_question.hint,
                    "lower_bound": answer.review_question.lower_bound,
                    "upper_bound": answer.review_question.upper_bound,
                    "parent_question_id": answer.review_question.parent_question_id,
                    "max_children": answer.review_question.max_children,
                    "answer_value": score,
                    "comment": answer.comment,
                }
            questions.append(answer_dict)

    review_event = {
        "body": {
            "id": review.id,
            "item_id": item_id,
            "user_id": user_id,
            "comment": comment,
            "status": status,
            "tags": tags
        },
        "requestContext": {
            "identity": {
                "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(user_id)
            }
        }
    }

    review_event['body']['questions'] = questions
    return review_event
