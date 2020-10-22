import crud.operations as operations
from crud.model import User, Item, Level, Review, ReviewPair, ReviewAnswer, ReviewQuestion
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
import test.unit.event_creator as event_creator
import test.unit.setup_scenarios as scenarios


def test_verification_process_best_case(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)
    session = scenarios.create_levels_junior_and_senior_detectives(session)

    junior_detective1 = operations.get_user_by_id("1", True, session)
    junior_detective2 = operations.get_user_by_id("2", True, session)
    junior_detective3 = operations.get_user_by_id("3", True, session)
    junior_detective4 = operations.get_user_by_id("4", True, session)

    senior_detective1 = operations.get_user_by_id("11", True, session)
    senior_detective2 = operations.get_user_by_id("12", True, session)
    senior_detective3 = operations.get_user_by_id("13", True, session)
    senior_detective4 = operations.get_user_by_id("14", True, session)

    users = operations.get_all_users_db(True, session)
    assert len(users) == 8

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item = operations.create_item_db(item, True, session)

    items = operations.get_all_items_db(True, session)
    assert len(items) == 1

    # Junior detectives accepting item
    operations.accept_item_db(junior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 1

    operations.accept_item_db(junior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 2

    operations.accept_item_db(junior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(junior_detective4, item, True, session)

    # Senior detectives accepting item
    operations.accept_item_db(senior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 1

    operations.accept_item_db(senior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 2

    operations.accept_item_db(senior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(senior_detective4, item, True, session)

    # Junior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, junior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, junior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 2
    assert item.in_progress_reviews_level_1 == 2

    review_event = event_creator.get_review_event(
        item.id, junior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 1
    assert item.in_progress_reviews_level_1 == 1

    review_event = event_creator.get_review_event(
        item.id, junior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 0
    assert item.in_progress_reviews_level_1 == 0

    # Senior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, senior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, senior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 2
    assert item.in_progress_reviews_level_2 == 2

    review_event = event_creator.get_review_event(
        item.id, senior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 1
    assert item.in_progress_reviews_level_2 == 1

    review_event = event_creator.get_review_event(
        item.id, senior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 0
    assert item.in_progress_reviews_level_2 == 0

    assert item.status == "closed"
    assert item.result_score == 1


def test_verification_process_worst_case(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)

    session = scenarios.create_levels_junior_and_senior_detectives(session)

    junior_detective1 = operations.get_user_by_id("1", True, session)
    junior_detective2 = operations.get_user_by_id("2", True, session)
    junior_detective3 = operations.get_user_by_id("3", True, session)
    junior_detective4 = operations.get_user_by_id("4", True, session)

    senior_detective1 = operations.get_user_by_id("11", True, session)
    senior_detective2 = operations.get_user_by_id("12", True, session)
    senior_detective3 = operations.get_user_by_id("13", True, session)
    senior_detective4 = operations.get_user_by_id("14", True, session)

    users = operations.get_all_users_db(True, session)
    assert len(users) == 8

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item = operations.create_item_db(item, True, session)

    items = operations.get_all_items_db(True, session)
    assert len(items) == 1

    # Junior detectives accepting item
    operations.accept_item_db(junior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 1

    operations.accept_item_db(junior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 2

    operations.accept_item_db(junior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(junior_detective4, item, True, session)

    # Senior detectives accepting item
    operations.accept_item_db(senior_detective1, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 1

    operations.accept_item_db(senior_detective2, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 2

    operations.accept_item_db(senior_detective3, item, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 3
    assert item.in_progress_reviews_level_2 == 3

    with pytest.raises(Exception):
        operations.accept_item_db(senior_detective4, item, True, session)

    # Junior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, junior_detective4.id, 4)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, junior_detective1.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 2
    assert item.in_progress_reviews_level_1 == 2

    review_event = event_creator.get_review_event(
        item.id, junior_detective2.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 1
    assert item.in_progress_reviews_level_1 == 1

    review_event = event_creator.get_review_event(
        item.id, junior_detective3.id, 4)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 0
    assert item.in_progress_reviews_level_1 == 0

    # Senior detectives reviewing item

    review_event = event_creator.get_review_event(
        item.id, senior_detective4.id, 1)
    response = app.submit_review(review_event, None, True, session)
    assert response['statusCode'] == 400

    review_event = event_creator.get_review_event(
        item.id, senior_detective1.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 2
    assert item.in_progress_reviews_level_2 == 2

    review_event = event_creator.get_review_event(
        item.id, senior_detective2.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_2 == 1
    assert item.in_progress_reviews_level_2 == 1

    review_event = event_creator.get_review_event(
        item.id, senior_detective3.id, 1)
    app.submit_review(review_event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)

    assert item.in_progress_reviews_level_2 == 0
    assert item.open_reviews_level_2 == 3
    assert item.open_reviews == 3
    assert item.result_score == None


def test_create_review(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)
    session = scenarios.create_levels_junior_and_senior_detectives(session)

    junior_detective1 = operations.get_user_by_id("1", True, session)
    junior_detective2 = operations.get_user_by_id("2", True, session)
    junior_detective3 = operations.get_user_by_id("3", True, session)
    junior_detective4 = operations.get_user_by_id("4", True, session)

    senior_detective1 = operations.get_user_by_id("11", True, session)
    senior_detective2 = operations.get_user_by_id("12", True, session)
    senior_detective3 = operations.get_user_by_id("13", True, session)
    senior_detective4 = operations.get_user_by_id("14", True, session)

    users = operations.get_all_users_db(True, session)
    assert len(users) == 8

    # Creating an item
    item = Item()
    item.content = "This item needs to be checked"
    item = operations.create_item_db(item, True, session)

    items = operations.get_all_items_db(True, session)
    assert len(items) == 1

    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 0
    assert len(review_pairs) == 0

    # Junior detectives accepting item
    event = event_creator.get_create_review_event(
        junior_detective1.id, item.id)
    response = app.create_review(event, None, True, session)
    assert response['statusCode'] == 201
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 1
    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 1
    assert len(review_pairs) == 1

    event = event_creator.get_create_review_event(
        junior_detective2.id, item.id)
    app.create_review(event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_1 == 2
    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 2
    assert len(review_pairs) == 2

    # Senior detective accepting item
    event = event_creator.get_create_review_event(
        senior_detective1.id, item.id)
    app.create_review(event, None, True, session)
    item = operations.get_item_by_id(item.id, True, session)
    assert item.open_reviews_level_1 == 3
    assert item.in_progress_reviews_level_2 == 1
    reviews = session.query(Review).all()
    review_pairs = session.query(ReviewPair).all()
    assert len(reviews) == 3
    assert len(review_pairs) == 2


def test_get_next_question(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app

    session = operations.get_db_session(True, None)
    session = scenarios.create_questions(session)

    pair = ReviewPair()
    pair.id = "Pair_1"
    session.add(pair)

    review = Review()
    review.id = "Review_1"
    session.add(review)

    pair.junior_review = review

    # event = event_creator.get_next_question_event(review.id)
    # repsonse = app.get_review_question(event, None, True, session)
    next_question = operations.get_next_question_db(
        review, None, True, session)
    assert next_question is not None

    # Add answer for question 2 that should trigger question 2b
    answer = ReviewAnswer()
    answer.id = "Answer_1"
    answer.review_question_id = "2"
    answer.answer = 1
    answer.review = review
    session.add(answer)
    assert len(review.review_answers) > 0

    question2 = session.query(ReviewQuestion).filter(
        ReviewQuestion.id == "2").one()

    next_question = operations.get_next_question_db(
        review, question2, True, session)
    assert next_question.id == "2b"

    answer2 = ReviewAnswer()
    answer2.id = "Answer_2"
    answer2.review_question_id = "1"
    answer2.answer = 3
    answer2.review = review
    session.add(answer2)

    question1 = session.query(ReviewQuestion).filter(
        ReviewQuestion.id == "1").one()
    next_question = operations.get_next_question_db(
        review, question1, True, session)
    assert next_question.id == "1a" or next_question.id == "1c"

    answer3 = ReviewAnswer()
    answer3.id = "Answer_3"
    answer3.review_question_id = next_question.id
    answer3.answer = 1
    answer3.review = review
    session.add(answer3)

    prev_question = next_question

    next_question = operations.get_next_question_db(
        review, prev_question, True, session)
    if prev_question.id == "1a":
        assert next_question.id == "1c"
    if prev_question.id == "1c":
        assert next_question.id == "1a"

    assert len(review.review_answers) == 3

    answer4 = ReviewAnswer()
    answer4.id = "Answer_4"
    answer4.review_question_id = "4"
    answer4.review = review

    answer5 = ReviewAnswer()
    answer5.id = "Answer_5"
    answer5.review_question_id = "5"
    answer5.review = review

    answer6 = ReviewAnswer()
    answer6.id = "Answer_6"
    answer6.review_question_id = "6"
    answer6.review = review

    answer7 = ReviewAnswer()
    answer7.id = "Answer_7"
    answer7.review_question_id = "7"
    answer7.review = review

    session.add(answer4)
    session.add(answer5)
    session.add(answer6)
    session.add(answer7)

    assert len(review.review_answers) == 7
    next_question = operations.get_next_question_db(
        review, prev_question, True, session)

    assert next_question == None

    # Create second review and append to pair
    review2 = Review()
    review2.id = "Review_2"
    session.add(review2)
    session.commit()
    pair.senior_review = review2
    session.merge(pair)
    session.commit()

    # Assert that question is within the range of questions in review one
    next_question = operations.get_next_question_db(
        review2, None, True, session)
    assert next_question.id in ["1", "2", "4", "5", "6", "7"]

    answer8 = ReviewAnswer()
    answer8.review = review2
    answer8.id = "Answer_8"
    answer8.answer = 1
    answer8.review_question = next_question
    session.add(answer8)
    session.commit()

    # Check for HTTP responses
    event = event_creator.get_next_question_event(review.id, "1")
    response = app.get_review_question(event, None, True, session)
    assert response['statusCode'] == 204

    event = event_creator.get_next_question_event(review2.id, next_question.id)
    response = app.get_review_question(event, None, True, session)
    assert response['statusCode'] == 200
