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


def get_all_submissions_db(is_test, session):

    session = get_db_session(is_test, session)
    submissions = session.query(Submission).all()
    return submissions


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
