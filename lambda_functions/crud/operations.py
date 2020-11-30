import json
import logging
import os
import random
import sqlite3
import statistics
import sys
from datetime import datetime, timedelta
from uuid import uuid4

import boto3
from crud.model import (
    URL, Base, Claimant, Entity, ExternalFactCheck, FactChecking_Organization,
    Item, ItemEntity, ItemKeyphrase, ItemSentiment, ItemURL, Keyphrase, Review,
    ReviewAnswer, ReviewQuestion, Sentiment, Submission,
    User, Level, ReviewPair)
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session, backref, relationship, sessionmaker

from . import helper, notifications

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_db_session(is_test, session) -> Session:
    """Returns a DB session

    Returns
    ------
    db: DB Connection
        The database connection
    """

    # put db session in seperate class

    if session != None:
        return session

    logger.info('New DB Session initiated')

    cluster_arn = "arn:aws:rds:eu-central-1:891514678401:cluster:serverless-db"
    secret_arn = "arn:aws:secretsmanager:eu-central-1:891514678401:secret:ServerlessDBSecret-7oczW5"

    if is_test == False:
        database_name = os.environ['DBNAME']
        db = create_engine('mysql+auroradataapi://:@/{0}'.format(database_name),
                           echo=True,
                           connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))
    else:
        def creator(): return sqlite3.connect(
            'file::memory:?cache=shared', uri=True, check_same_thread=False)
        db = create_engine('sqlite://', creator=creator)
        Base.metadata.create_all(db)

    Session = sessionmaker(bind=db, expire_on_commit=False)
    session = Session()

    return session


def create_item_db(item, is_test, session):
    """Inserts a new item into the database

    Parameters
    ----------
    item: Item, required
        The item to be inserted

    Returns
    ------
    item: Item
        The inserted item
    """
    session = get_db_session(is_test, session)

    item.id = str(uuid4())
    item.open_reviews = 4
    item.open_reviews_level_1 = 4
    item.open_reviews_level_2 = 4
    item.in_progress_reviews_level_1 = 0
    item.in_progress_reviews_level_2 = 0
    item.status = "open"
    session.add(item)
    session.commit()

    return item


def update_object_db(obj, is_test, session):
    """Updates an existing item in the database

    Parameters
    ----------
    obj: object to be merged in the DB, required
        The item to be updates

    Returns
    ------
    obj: The merged object
    """
    session = get_db_session(is_test, session)

    session.merge(obj)
    session.commit()
    return obj


def get_all_items_db(is_test, session):
    """Returns all items from the database

    Returns
    ------
    items: Item[]
        The items
    """
    session = get_db_session(is_test, session)
    items = session.query(Item).all()
    return items


def get_item_by_content_db(content, is_test, session):
    """Returns an item with the specified content from the database

        Returns
        ------
        item: Item
            The item
        Null, if no item was found
        """
    session = get_db_session(is_test, session)
    item = session.query(Item).filter(Item.content == content).first()
    if item is None:
        raise Exception("No item found.")
    return item


def get_item_by_id(id, is_test, session):
    """Returns an item by its id

    Parameters
    ----------
    id: str, required
        The id of the item

    Returns
    ------
    item: Item
        The item
    """
    session = get_db_session(is_test, session)
    item = session.query(Item).get(id)

    # Uncomment to test telegram user notification
    # notifications.notify_telegram_users(is_test, session, item)

    return item


def get_old_reviews_in_progress(is_test, session):
    old_time = helper.get_date_time_one_hour_ago(is_test)
    session = get_db_session(is_test, session)
    rips = session.query(Review).filter(
        Review.start_timestamp < old_time, Review.status == "in_progress").all()
    return rips


def get_factcheck_by_itemid_db(id, is_test, session):
    """Returns factchecks referenced by an item id

    Parameters
    ----------
    id: str, required
        The id of the item

    Returns
    ------
    factcheck: ExternalFactCheck
        The first factcheck referenced by the item
        None if no factcheck referenced by the item
    """
    session = get_db_session(is_test, session)
    factcheck = session.query(ExternalFactCheck).select_from(Item).\
        join(Item.factchecks).\
        filter(Item.id == id)
    return factcheck.first()


def create_submission_db(submission, is_test, session):
    """Inserts a new submission into the database

    Parameters
    ----------
    submission: Submission, required
        The submission to be inserted

    Returns
    ------
    submission: Submission
        The inserted submission
    """
    session = get_db_session(is_test, session)

    submission.id = str(uuid4())
    submission.submission_date = helper.get_date_time_now(is_test)

    session.add(submission)
    session.commit()

    return submission


def get_all_submissions_db(is_test, session):

    session = get_db_session(is_test, session)
    submissions = session.query(Submission).all()
    return submissions


def create_user_db(user, is_test, session):
    """Inserts a new user into the database

    Parameters
    ----------
    user: User, required
        The user to be inserted

    Returns
    ------
    user: User
        The inserted user
    """
    if session == None:
        session = get_db_session(is_test, session)

    user.score = 0
    user.level_id = 1
    user.experience_points = 0
    session.add(user)
    session.commit()

    return user


def get_all_users_db(is_test, session):
    """Returns all users from the database

    Returns
    ------
    users: User[]
        The users
    """
    if session == None:
        session = get_db_session(is_test, session)
    users = session.query(User).all()
    return users


def get_user_by_id(id, is_test, session):
    """Returns a user by their id

    Parameters
    ----------
    id: str, required
        The id of the user

    Returns
    ------
    user: User
        The user
    """

    session = get_db_session(is_test, session)
    user = session.query(User).get(id)
    return user


def delete_user(event, is_test, session):
    """Deletes a user from the database.

    Parameters
    ----------
    user_id: str, required
             The id of the user

    Returns
    ------
    nothing
    """
    if session is None:
        session = get_db_session(is_test, session)

    user_id = helper.cognito_id_from_event(event)
    user = session.query(User).get(user_id)

    if(user == None):
        raise Exception(
            f"User with id {user_id} could not be found in database.")

    client = boto3.client('cognito-idp')
    client.admin_delete_user(
        UserPoolId=event['requestContext']['identity']['cognitoAuthenticationProvider'].split(',')[
            0].split('amazonaws.com/')[1],
        Username=user.name
    )

    session.delete(user)
    session.commit()


def get_all_reviews_db(is_test, session):
    """Returns all reviews from the database

    Returns
    ------
    reviews: Review[]
        The reviews
    """

    session = get_db_session(is_test, session)
    reviews = session.query(Review).all()
    return reviews


def get_reviews_by_item_id(item_id, is_test, session):

    session = get_db_session(is_test, session)
    reviews = session.query(Review).filter(Review.item_id == item_id)
    return reviews


def get_good_reviews_by_item_id(item_id, is_test, session):
    session = get_db_session(is_test, session)
    reviews = session.query(Review).filter(Review.item_id == item_id).filter(
        Review.belongs_to_good_pair == True)
    return reviews


def create_review_answer_db(review_answer, is_test, session):
    """Inserts a new review answer into the database

    Parameters
    ----------
    review_answer: ReviewAnswer, required
        The review answer to be inserted

    Returns
    ------
    review_answer: reviewAnswer
        The inserted review answer
    """

    session = get_db_session(is_test, session)

    review_answer.id = str(uuid4())
    session.add(review_answer)
    session.commit()
    session.expire_all()

    return review_answer


def create_review_answer_set_db(review_answers, review_id, is_test, session):
    session = get_db_session(is_test, session)
    for review_answer in review_answers:
        review_answer.id = str(uuid4())
        review_answer.review_id = review_id
        session.add(review_answer)
    session.commit()


def get_all_review_answers_db(is_test, session):
    """Returns all review answers from the database

    Returns
    ------
    review_answers: ReviewAnswer[]
        The review answers
    """

    session = get_db_session(is_test, session)
    review_answers = session.query(ReviewAnswer).all()
    return review_answers


def get_review_answers_by_review_id_db(review_id, is_test, session):
    """Returns all review answers from the database that belong to the specified review

    Returns
    ------
    review_answers: ReviewAnswer[]
        The review answers
    """

    session = get_db_session(is_test, session)
    review_answers = session.query(ReviewAnswer).filter(
        ReviewAnswer.review_id == review_id)
    return review_answers


def get_all_review_questions_db(is_test, session):
    """Returns all review answers from the database

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions
    """

    session = get_db_session(is_test, session)
    review_questions = session.query(ReviewQuestion).all()
    return review_questions


def give_experience_point(user_id, is_test, session):
    user = get_user_by_id(user_id, is_test, session)
    user.experience_points = user.experience_points + 1
    new_level = session.query(Level) \
        .filter(Level.required_experience_points <= user.experience_points) \
        .order_by(Level.required_experience_points.desc()) \
        .first()

    if new_level != user.level_id:
        user.level_id = new_level.id
    update_object_db(user, is_test, session)


def get_pair_difference(junior_review, peer_review, is_test, session):

    peer_review_answers = get_review_answers_by_review_id_db(
        peer_review.id, is_test, session)
    junior_review_answers = get_review_answers_by_review_id_db(
        junior_review.id, is_test, session)

    answers_length = peer_review_answers.count()
    relevant_answers = 0

    junior_review_score_sum = 0
    peer_review_score_sum = 0

    for i in range(1, answers_length + 1, 1):
        junior_answer = junior_review_answers.filter(
            ReviewAnswer.review_question_id == i).one().answer
        peer_answer = peer_review_answers.filter(
            ReviewAnswer.review_question_id == i).one().answer
        if junior_answer > 0 and peer_answer > 0:
            junior_review_score_sum = junior_review_score_sum + junior_answer
            peer_review_score_sum = peer_review_score_sum + peer_answer
            relevant_answers = relevant_answers + 1

    junior_review_average = junior_review_score_sum / relevant_answers
    peer_review_average = peer_review_score_sum / relevant_answers

    difference = abs(junior_review_average - peer_review_average)
    return difference


def compute_item_result_score(item_id, is_test, session):
    pairs = get_review_pairs_by_item(item_id, is_test, session)

    average_scores = []
    for pair in list(filter(lambda p: p.is_good, pairs)):
        average_scores.append(pair.variance)

    result = statistics.median(average_scores)
    return result


def get_open_items_for_user_db(user, num_items, is_test, session):
    """Retreives a list of open items (in random order) to be reviewed by a user.

    Parameters
    ----------
    user: User
        The user that should receive a case
    num_items: int
        The (maximum) number of open items to be retreived

    Returns
    ------
    items: Item[]
        The list of open items for the user
    """

    session = get_db_session(is_test, session)
    items = []

    # If review in progress exists for user, return the corresponding item(s)
    result = session.query(Review).filter(
        Review.user_id == user.id, Review.status == "in_progress").limit(num_items)
    if result.count() > 0:
        for rip in result:
            item_id = rip.item_id
            item = get_item_by_id(item_id, is_test, session)
            items.append(item)
        # shuffle list order
        random.shuffle(items)
        return items

    if user.level_id > 1:
        # Get open items for senior review
        result = session.query(Item) \
            .filter(Item.open_reviews_level_2 > Item.in_progress_reviews_level_2) \
            .filter(~Item.reviews.any(Review.user_id == user.id)) \
            .order_by(Item.open_timestamp.asc()) \
            .limit(num_items).all()

        # If open items are available, return them
        if len(result) > 0:
            for item in result:
                items.append(item)
            random.shuffle(items)
            return items

    # Get open items for junior review and return them
    result = session.query(Item) \
        .filter(Item.open_reviews_level_1 > Item.in_progress_reviews_level_1) \
        .filter(~Item.reviews.any(Review.user_id == user.id)) \
        .order_by(Item.open_timestamp.asc()) \
        .limit(num_items).all()

    for item in result:
        items.append(item)
    random.shuffle(items)
    return items


def get_claimant_by_name_db(claimant_name, is_test, session):
    """Returns a claimant with the specified name

        Returns
        ------
        claimant: Claimant
            An url referenced in an item
        Null, if no claimant was found
        """
    session = get_db_session(is_test, session)
    claimant = session.query(Claimant).filter(
        Claimant.claimant == claimant_name).first()
    if claimant is None:
        raise Exception("No claimant found.")
    return claimant


def get_url_by_content_db(content, is_test, session):
    """Returns an url with the specified content from the database

        Returns
        ------
        url: URL
            An url referenced in an item
        Null, if no url was found
        """
    session = get_db_session(is_test, session)
    url = session.query(URL).filter(URL.url == content).first()
    if url is None:
        raise Exception("No url found.")
    return url


def get_entity_by_content_db(content, is_test, session):
    """Returns an entity with the specified content from the database

        Returns
        ------
        entity: Entity
            An entity of an item
        Null, if no entity was found
        """
    session = get_db_session(is_test, session)
    entity = session.query(Entity).filter(Entity.entity == content).first()
    if entity is None:
        raise Exception("No entity found.")
    return entity


def get_organization_by_content_db(content, is_test, session):
    """Returns the organization publishing fact checks

        Returns
        ------
        org: FactChecking_Organization
        Null, if no org was found
        """
    session = get_db_session(is_test, session)
    org = session.query(FactChecking_Organization).filter(
        FactChecking_Organization.name == content).first()
    if org is None:
        raise Exception("No Organization found.")
    return org


def get_factcheck_by_url_and_item_db(factcheck_url, item_id, is_test, session):
    """Returns the factcheck publishing fact checks

        Returns
        ------
        factcheck: ExternalFactCheck
        Null, if no factcheck was found
        """
    session = get_db_session(is_test, session)
    factcheck = session.query(ExternalFactCheck).filter(ExternalFactCheck.url == factcheck_url,
                                                        ExternalFactCheck.item_id == item_id).first()
    if factcheck is None:
        raise Exception("No Factcheck found.")
    return factcheck


def get_itemurl_by_url_and_item_db(url_id, item_id, is_test, session):
    """Returns the itemurl for an item and url

        Returns
        ------
        itemurl: ItemURL
        Null, if no itemurl was found
        """
    session = get_db_session(is_test, session)
    itemurl = session.query(ItemURL).filter(ItemURL.url_id == url_id,
                                            ItemURL.item_id == item_id).first()
    if itemurl is None:
        raise Exception("No ItemURL found.")
    return itemurl


def get_itementity_by_entity_and_item_db(entity_id, item_id, is_test, session):
    """Returns the itementity for an item and entity

        Returns
        ------
        itementity: ItemEntity
        Null, if no itementity was found
    """
    session = get_db_session(is_test, session)
    itementity = session.query(ItemEntity).filter(ItemEntity.entity_id == entity_id,
                                                  ItemEntity.item_id == item_id).first()
    if itementity is None:
        raise Exception("No ItemEntity found.")
    return itementity


def get_entities_by_itemid_db(item_id, is_test, session):
    """Returns the entities for an item

        Returns
        ------
        entities: Entity[]
        Null, if no entity was found
    """
    session = get_db_session(is_test, session)
    entities = session.query(Entity).\
        join(ItemEntity).\
        filter(ItemEntity.item_id == item_id).\
        filter(ItemEntity.entity_id == Entity.id).\
        all()
    return entities


def get_sentiment_by_content_db(content, is_test, session):
    """Returns the sentiment with the specified content from the database

        Returns
        ------
        sentiment: Sentiment
            The sentiment of an item
        Null, if no sentiment was found
        """
    session = get_db_session(is_test, session)
    sentiment = session.query(Sentiment).filter(
        Sentiment.sentiment == content).first()
    if sentiment is None:
        raise Exception("No sentiment found.")
    return sentiment


def get_itemsentiment_by_sentiment_and_item_db(sentiment_id, item_id, is_test, session):
    """Returns the itemsentiment for an item and sentiment

        Returns
        ------
        itemsentiment: ItemSentiment
        Null, if no itemsentiment was found
    """
    session = get_db_session(is_test, session)
    itemsentiment = session.query(ItemSentiment).filter(ItemSentiment.sentiment_id == sentiment_id,
                                                        ItemSentiment.item_id == item_id).first()
    if itemsentiment is None:
        raise Exception("No Item Sentiment found.")
    return itemsentiment


def get_phrase_by_content_db(content, is_test, session):
    """Returns a keyphrase with the specified content from the database

        Returns
        ------
        keyphrase: Keyphrase
            A key phrase of an item
        Null, if no key phrase was found
        """
    session = get_db_session(is_test, session)
    phrase = session.query(Keyphrase).filter(
        Keyphrase.phrase == content).first()
    if phrase is None:
        raise Exception("No key phrase found.")
    return phrase


def get_itemphrase_by_phrase_and_item_db(phrase_id, item_id, is_test, session):
    """Returns the itemkeyphrase for an item and keyphrase

        Returns
        ------
        itemphrase: ItemKeyphrase
        Null, if no itemphrase was found
    """
    session = get_db_session(is_test, session)
    itemphrase = session.query(ItemKeyphrase).filter(ItemKeyphrase.keyphrase_id == phrase_id,
                                                     ItemKeyphrase.item_id == item_id).first()
    if itemphrase is None:
        raise Exception("No ItemKeyphrase found.")
    return itemphrase


def get_phrases_by_itemid_db(item_id, is_test, session):
    """Returns the key phrases for an item

        Returns
        ------
        phrases: Keyphrase[]
        Null, if no entity was found
    """
    session = get_db_session(is_test, session)
    phrases = session.query(Keyphrase).\
        join(ItemKeyphrase).\
        filter(ItemKeyphrase.item_id == item_id).\
        filter(ItemKeyphrase.keyphrase_id == Keyphrase.id).\
        all()
    return phrases


def delete_old_reviews_in_progress(rips, is_test, session):
    for rip in rips:
        item = get_item_by_id(rip.item_id, is_test, session)
        if rip.is_peer_review == True:
            item.in_progress_reviews_level_2 -= 1
        else:
            item.in_progress_reviews_level_1 -= 1
        session.merge(item)
        session.delete(rip)
    session.commit()


def accept_item_db(user, item, is_test, session) -> Review:
    """Accepts an item for review

    Parameters
    ----------
    user: User
        The user that reviews the item
    item: Item
        The item to be reviewed by the user

    Returns
    ------
    item: Item
        The case to be assigned to the user
    """
    # If a ReviewInProgress exists for the user, return
    try:
        review = session.query(Review).filter(
            Review.user_id == user.id, Review.status == "in_progress", Review.item_id == item.id).one()
        return review
    except:
        pass

    # If the amount of reviews in progress equals the amount of reviews needed, raise an error
    if item.in_progress_reviews_level_1 >= item.open_reviews_level_1:
        if user.level_id > 1:
            if item.in_progress_reviews_level_2 >= item.open_reviews_level_2:
                raise Exception(
                    'Item cannot be accepted since enough other detecitves are already working on the case')
        else:
            raise Exception(
                'Item cannot be accepted since enough other detecitves are already working on the case')
    # Create a new ReviewInProgress
    rip = Review()
    rip.id = str(uuid4())
    rip.item_id = item.id
    rip.user_id = user.id
    rip.start_timestamp = helper.get_date_time_now(is_test)
    rip.status = "in_progress"
    session.add(rip)
    session.commit()

    # If a user is a senior, the review will by default be a senior review,
    # except if no senior reviews are needed
    if user.level_id > 1 and item.open_reviews_level_2 > item.in_progress_reviews_level_2:
        rip.is_peer_review = True
        item.in_progress_reviews_level_2 = item.in_progress_reviews_level_2 + 1

        # Check if a pair with open senior review exists
        pair_found = False
        for pair in item.review_pairs:
            if pair.senior_review_id == None:
                pair.senior_review_id = rip.id
                pair_found = True
                session.merge(pair)
                break

        # Create new pair, if review cannot be attached to existing pair
        if pair_found == False:
            pair = ReviewPair()
            pair.id = str(uuid4())
            pair.senior_review_id = rip.id
            item.review_pairs.append(pair)
            session.merge(pair)

    # If review is junior review
    else:
        rip.is_peer_review = False
        item.in_progress_reviews_level_1 = item.in_progress_reviews_level_1 + 1

        # Check if a pair with open junior review exists
        pair_found = False
        for pair in item.review_pairs:
            if pair.junior_review_id == None:
                pair.junior_review_id = rip.id
                pair_found = True
                session.merge(pair)
                break

        # Create new pair, if review cannot be attached to existing pair
        if pair_found == False:
            pair = ReviewPair()
            pair.id = str(uuid4())
            pair.junior_review_id = rip.id
            item.review_pairs.append(pair)
            session.merge(pair)

    session.merge(rip)
    session.merge(item)
    session.commit()
    return rip


def get_next_question_db(review, previous_question, is_test, session):
    session = get_db_session(is_test, session)

    if len(review.review_answers) == 7:
        return None

    previous_question_ids = []
    for answer in review.review_answers:
        previous_question_ids.append(answer.review_question_id)

    # Check for conditional question
    if previous_question != None:
        parent_question_found = False
        # Determine relevant parent question
        if len(previous_question.child_questions) > 0:
            parent_question_found = True
            parent_question = previous_question
        if previous_question.parent_question != None:
            parent_question_found = True
            parent_question = previous_question.parent_question

        if parent_question_found:
            parent_answer = session.query(ReviewAnswer).filter(
                ReviewAnswer.review_id == review.id, ReviewAnswer.review_question_id == parent_question.id).one()

            child_questions = parent_question.child_questions

            for child_question in child_questions:
                # Check if question has already been answered
                if child_question.id not in previous_question_ids:
                    # Check answer triggers child question
                    if parent_answer.answer <= child_question.upper_bound and parent_answer.answer >= child_question.lower_bound:
                        return child_question

    partner_review = get_partner_review(review, is_test, session)

    if partner_review != None:
        partner_review_question_ids = []
        # Get all parent question ids from partner review
        for answer in partner_review.review_answers:
            if answer.review_question.parent_question_id == None:
                partner_review_question_ids.append(answer.review_question_id)
        # Find question
        for question_id in partner_review_question_ids:
            if question_id not in previous_question_ids:
                return get_review_question_by_id(question_id, is_test, session)

    # Check how many questions are still needed
    remaining_questions = 7 - len(review.review_answers)

    # Get all questions
    all_questions = get_all_review_questions_db(is_test, session)
    random.shuffle(all_questions)

    for question in all_questions:
        # Check if question has already been answered
        if question.id not in previous_question_ids:
            # Check if question is a parent question
            if question.parent_question == None:
                # Check if question does not exceed limit with child question
                if question.max_children and remaining_questions > question.max_children:
                    return question

    raise Exception("No question could be returned")


def get_review_pair(review, is_test, session) -> ReviewPair:
    session = get_db_session(is_test, session)

    return session.query(ReviewPair).filter(or_(ReviewPair.junior_review_id == review.id, ReviewPair.senior_review_id == review.id)).first()


def get_partner_review(review, is_test, session):
    session = get_db_session(is_test, session)

    pair = session.query(ReviewPair).filter(or_(ReviewPair.junior_review_id ==
                                                review.id, ReviewPair.senior_review_id == review.id)) \
        .first()

    try:
        if review.id == pair.junior_review_id:
            return get_review_by_id(pair.senior_review_id, is_test, session)

        if review.id == pair.senior_review_id:
            return get_review_by_id(pair.junior_review_id, is_test, session)
    except:
        return None


def get_all_closed_items_db(is_test, session):
    """Gets all closed items

    Returns
    ------
    items: Item[]
        The closed items
    """

    session = get_db_session(is_test, session)

    items = session.query(Item).filter(Item.status == 'closed').all()
    return items


def get_review_in_progress(user_id, item_id, is_test, session):
    session = get_db_session(is_test, session)
    try:
        review_in_progress = session.query(Review).filter(
            Review.item_id == item_id,
            Review.user_id == user_id, Review.status == "in_progress").one()
        return review_in_progress

    except Exception as e:
        raise Exception(
            "Could not get review_in_progress. Either none or multiple objects exist." + e)


def review_submission_db(review, review_answers, is_test, session):

    # Gets review_in_progress. If none exists, raise an exception
    try:
        review = get_review_in_progress(
            review.user_id, review.item_id, is_test, session)
    except Exception as e:
        raise Exception("Could not get review_in_progress" + e)

    review.finish_timestamp = helper.get_date_time_now(is_test)
    review.status = "closed"

    session.merge(review)
    # review = create_review_db(review, is_test, session)
    create_review_answer_set_db(
        review_answers, review.id, is_test, session)
    session.commit()

    item = Item()
    item = get_item_by_id(review.item_id, is_test, session)
    if review.is_peer_review == True:
        item.open_reviews_level_2 -= 1
        item.in_progress_reviews_level_2 -= 1
    else:
        item.open_reviews_level_1 -= 1
        item.in_progress_reviews_level_1 -= 1

    item = update_object_db(item, is_test, session)
    return item


def build_review_pairs(item, is_test, session):
    junior_reviews = session.query(Review).filter(
        Review.item_id == item.id,
        Review.is_peer_review == False
    )
    senior_reviews = session.query(Review).filter(
        Review.item_id == item.id,
        Review.is_peer_review == True
    )

    if senior_reviews.count() != junior_reviews.count():
        raise Exception(
            "Number of junior reviews does not equal number of senior reviews.")
    for senior_review in senior_reviews:
        junior_review = junior_reviews.first()
        junior_review.peer_review_id = senior_review.id

        difference = get_pair_difference(
            junior_review, senior_review, is_test, session)

        if difference < 1:
            junior_review.belongs_to_good_pair = True
            senior_review.belongs_to_good_pair = True
            item.open_reviews -= 1

        else:
            junior_review.belongs_to_good_pair = False
            senior_review.belongs_to_good_pair = False

        session.merge(junior_review)
        session.merge(senior_review)
        # session.commit()

        junior_reviews = junior_reviews.filter(
            Review.id != junior_review.id
        )

    if item.open_reviews <= 0:
        item.status = "closed"
        item.result_score = compute_item_result_score(
            item.id, is_test, session)

        # Notify email and telegram users
        notifications.notify_users(is_test, session, item)

    else:
        item.open_reviews_level_1 = item.open_reviews
        item.open_reviews_level_2 = item.open_reviews

    session.merge(item)
    session.commit()
    return item


def get_submissions_by_item_id(item_id, is_test, session):

    session = get_db_session(is_test, session)
    submissions = session.query(Submission).filter(
        Submission.item_id == item_id).all()
    return submissions


def get_review_by_id(review_id, is_test, session) -> Review:
    session = get_db_session(is_test, session)

    review = session.query(Review).filter(
        Review.id == review_id
    ).one()

    return review


def get_review_question_by_id(question_id, is_test, session):
    session = get_db_session(is_test, session)

    question = session.query(ReviewQuestion).filter(
        ReviewQuestion.id == question_id
    ).one()

    return question


def get_partner_answer(partner_review: Review, question_id, is_test, session) -> ReviewAnswer:
    session = get_db_session(is_test, session)

    review_answer = session.query(ReviewAnswer).filter(
        ReviewAnswer.review_id == partner_review.id,
        ReviewAnswer.review_question_id == question_id).first()

    return review_answer


def compute_variance(pair: ReviewPair) -> float:
    junior_review_average = compute_review_result(
        pair.junior_review.review_answers)
    senior_review_average = compute_review_result(
        pair.senior_review.review_answers)

    return abs(junior_review_average - senior_review_average)


def compute_review_result(review_answers):
    if(review_answers == None):
        raise TypeError('ReviewAnswers is None!')

    if not isinstance(review_answers, list):
        raise TypeError('ReviewAnswers is not a list')

    if(len(review_answers) <= 0):
        raise ValueError('ReviewAnswers is an empty list')

    answers = (review_answer.answer for review_answer in review_answers)

    return sum(answers) / len(review_answers)


def get_review_pairs_by_item(item_id, is_test, session):
    session = get_db_session(is_test, session)

    pairs = session.query(ReviewPair).filter(
        ReviewPair.item_id == item_id).all()

    return pairs
