
def get_create_review_event(user_id, item_id):

    accept_event = {
        "queryStringParameters": {
            "item_id": item_id
        },
        "requestContext": {
            "identity": {
                "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(user_id)
            }
        }
    }
    return accept_event


def get_review_event(item_id, user_id, score):
    review_event = {
        "body": {
            "item_id": item_id,
            "review_answers": [
                {
                    "review_question_id": "1",
                    "answer": score
                },
                {
                    "review_question_id": "2",
                    "answer": score
                },
                {
                    "review_question_id": "3",
                    "answer": score
                },
                {
                    "review_question_id": "4",
                    "answer": score
                },
                {
                    "review_question_id": "5",
                    "answer": score
                },
                {
                    "review_question_id": "6",
                    "answer": score
                },
                {
                    "review_question_id": "7",
                    "answer": score
                },
                {
                    "review_question_id": "8",
                    "answer": score
                },
                {
                    "review_question_id": "9",
                    "answer": score
                },
                {
                    "review_question_id": "10",
                    "answer": score
                },
                {
                    "review_question_id": "11",
                    "answer": score
                },
                {
                    "review_question_id": "12",
                    "answer": score
                },
                {
                    "review_question_id": "13",
                    "answer": score
                }
            ]
        },
        "requestContext": {
            "identity": {
                "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(user_id)
            }
        }
    }
    return review_event
