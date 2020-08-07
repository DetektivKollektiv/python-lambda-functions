import os
from uuid import uuid4
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine
from crud.model import *
from datetime import datetime, timedelta

import json
import random
import statistics


def body_to_object(body, object):
    """Uses the request body to set the attributes of the specified object.

    Parameters
    ----------
    body: str, dict
        The request body (str or dict)
    object: Item, User, Review, Submission, etc.
        The object, e.g. an instance of the class Item or User

    Returns
    ------
    obj: Object
        The object with the set attributes
    """

    # Deserialize if body is string (--> Lambda called by API Gateway)
    if isinstance(body, str): 
        body_dict = json.loads(body)
    else: 
        body_dict = body

    # Load request body as dict and transform to Item object
    for key in body_dict:
        if type(body_dict[key]) != list:
            setattr(object, key, body_dict[key])

    return object


def set_cors(response, event):
    """Adds a CORS header to a response according to the headers found in the event.

    Parameters
    ----------
    response: dict
        The response to be modified
    event: dict
        The Lambda event

    Returns
    ------
    response: dict
        The modified response
    """
    source_origin = None
    allowed_origins = os.environ['CORS_ALLOW_ORIGIN'].split(',')
    
    if 'headers' in event:
        if 'Origin' in event['headers']:
            source_origin = event['headers']['Origin']
        if 'origin' in event['headers']:
            source_origin = event['headers']['origin']
        
        if source_origin and source_origin in allowed_origins:
            if 'headers' not in response:
                response['headers'] = {}

            response['headers']['Access-Control-Allow-Origin'] = source_origin           

    return response


def cognito_id_from_event(event):
    """Extracts the cognito user id (=sub) from the event.

    Parameters
    ----------
    event: dict
        The Lambda event

    Returns
    ------
    user_id: str
        The user id
    """
    user_id = str(event['requestContext']['identity']['cognitoAuthenticationProvider']).split("CognitoSignIn:",1)[1]
    return user_id


def get_db_session():
    """Returns a DB session

    Returns
    ------
    db: DB Connection
        The database connection
    """

    # TODO Environment variables, put db session in seperate class
    cluster_arn = "arn:aws:rds:eu-central-1:891514678401:cluster:serverless-db"
    secret_arn = "arn:aws:secretsmanager:eu-central-1:891514678401:secret:ServerlessDBSecret-7oczW5"

    database_name = os.environ['DBNAME']

    db = create_engine('mysql+auroradataapi://:@/{0}'.format(database_name),
                       echo=True,
                       connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))

    Session = sessionmaker(bind=db)
    session = Session()

    return session


def create_item_db(item):
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

    session = get_db_session()

    item.id = str(uuid4())
    item.open_reviews = 3
    item.status = "needs_junior"
    session.add(item)
    session.commit()

    return item


def update_object_db(obj):
    """Updates an existing item in the database

    Parameters
    ----------
    obj: object to be merged in the DB, required
        The item to be updates

    Returns
    ------
    obj: The merged object
    """

    session = get_db_session()

    session.merge(obj)
    session.commit()

    return obj


def get_all_items_db():
    """Returns all items from the database

    Returns
    ------
    items: Item[]
        The items
    """

    session = get_db_session()
    items = session.query(Item).all()
    return items


def get_item_by_content_db(content):
    """Returns an item with the specified content from the database

        Returns
        ------
        item: Item
            The item
        Null, if no item was found
        """
    session = get_db_session()
    item = session.query(Item).filter(Item.content == content).first()
    if item is None:
        raise Exception("No item found.")
    return item


def get_item_by_id(id):
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

    session = get_db_session()
    item = session.query(Item).get(id)
    return item


def get_locked_items():
    session = get_db_session()
    items = session.query(Item).filter(
        Item.status.in_(['locked_by_junior','locked_by_senior'])
        )
    return items

def create_submission_db(submission):
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
    session = get_db_session()

    submission.id = str(uuid4())
    submission.submission_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    session.add(submission)
    session.commit()

    return submission


def get_all_submissions_db():

    session = get_db_session()
    submissions = session.query(Submission).all()
    return submissions


def create_user_db(user):
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

    session = get_db_session()

    user.score = 0
    user.level = 1
    user.experience_points = 0
    session.add(user)
    session.commit()

    return user


def get_all_users_db():
    """Returns all users from the database

    Returns
    ------
    users: User[]
        The users
    """

    session = get_db_session()
    users = session.query(User).all()
    return users


def get_user_by_id(id):
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

    session = get_db_session()
    user = session.query(User).get(id)
    return user


def create_review_db(review):
    """Inserts a new review into the database

    Parameters
    ----------
    review: Review, required
        The review to be inserted

    Returns
    ------
    review: Review
        The inserted review
    """

    session = get_db_session()

    review.id = str(uuid4())
    session.add(review)
    session.commit()

    return review


def get_all_reviews_db():
    """Returns all reviews from the database

    Returns
    ------
    reviews: Review[]
        The reviews
    """

    session = get_db_session()
    reviews = session.query(Review).all()
    return reviews

def get_reviews_by_item_id(item_id):

    session = get_db_session()
    reviews = session.query(Review).filter(Review.item_id == item_id)
    return reviews

def get_good_reviews_by_item_id(item_id):
    session = get_db_session()
    reviews = session.query(Review).filter(Review.item_id == item_id).filter(Review.belongs_to_good_pair == True)
    return reviews
    

def get_review_by_peer_review_id_db(peer_review_id):
    """Returns a review from the database with the specified peer review id
    
    Parameters
    ----------
    peer_review_id: Str, required
        The peer review id to query for

    Returns
    ------
    review: Review
        The review
    """

    session = get_db_session()
    review = session.query(Review).filter(Review.peer_review_id == peer_review_id).first()
    return review


def create_review_answer_db(review_answer):
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

    session = get_db_session()

    review_answer.id = str(uuid4())
    session.add(review_answer)
    session.commit()

    return review_answer

def create_review_answer_set_db(review_answers):
    session = get_db_session()
    for review_answer in review_answers:
        review_answer.id = str(uuid4())
        session.add(review_answer)    
    session.commit()


def get_all_review_answers_db():
    """Returns all review answers from the database

    Returns
    ------
    review_answers: ReviewAnswer[]
        The review answers
    """

    session = get_db_session()
    review_answers = session.query(ReviewAnswer).all()
    return review_answers

def get_review_answers_by_review_id_db(review_id):
    """Returns all review answers from the database that belong to the specified review

    Returns
    ------
    review_answers: ReviewAnswer[]
        The review answers
    """

    session = get_db_session()
    review_answers = session.query(ReviewAnswer).filter(ReviewAnswer.review_id == review_id)
    return review_answers


def get_all_review_questions_db():
    """Returns all review answers from the database

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions
    """

    session = get_db_session()
    review_questions = session.query(ReviewQuestion).all()
    return review_questions


def give_experience_point(user_id):    
    user = get_user_by_id(user_id)
    user.experience_points = user.experience_points + 1
    if user.experience_points >= 5:
        user.level = 2
    update_object_db(user)

def check_if_review_still_needed(item_id, user_id, is_peer_review):
    
    item = get_item_by_id(item_id)
    status = item.status
    if is_peer_review == True:
        if status == "locked_by_senior" and item.locked_by_user == user_id:
            return True
        else:
            return False
    if is_peer_review == False:
        if status == "locked_by_junior" and item.locked_by_user == user_id:
            return True
        else:
            return False

def close_open_junior_review(item_id, peer_review_id):
    """Returns all reviews from the database that belong to the item with the specified id
    
    Parameters
    ----------
    item_id: Str, required
        The item id to query for
    
    Returns
    ------
    review: Review
        The open junior review
    """
    session = get_db_session()
    query_result = session.query(Review).filter(
        Review.item_id == item_id,
        Review.is_peer_review == False,
        Review.peer_review_id == None
        )
    open_junior_review = query_result.one()
    open_junior_review.peer_review_id = peer_review_id
    update_object_db(open_junior_review)

def get_pair_difference(review_id):
    junior_review = get_review_by_peer_review_id_db(review_id)
    
    peer_review_answers = get_review_answers_by_review_id_db(review_id)
    junior_review_answers = get_review_answers_by_review_id_db(junior_review.id)

    answers_length = peer_review_answers.count()
    relevant_answers = 0

    junior_review_score_sum = 0
    peer_review_score_sum = 0

    for i in range(1,answers_length + 1,1):
        junior_answer = junior_review_answers.filter(ReviewAnswer.review_question_id == i).one().answer
        peer_answer = peer_review_answers.filter(ReviewAnswer.review_question_id == i).one().answer
        if junior_answer > 0 and peer_answer > 0:
            junior_review_score_sum = junior_review_score_sum + junior_answer
            peer_review_score_sum = peer_review_score_sum + peer_answer
            relevant_answers = relevant_answers + 1

    junior_review_average = junior_review_score_sum / relevant_answers
    peer_review_average = peer_review_score_sum / relevant_answers

    difference = abs(junior_review_average - peer_review_average)
    return difference

def set_belongs_to_good_pair_db(review, belongs_to_good_pair):
    peer_review = review
    junior_review = get_review_by_peer_review_id_db

    if belongs_to_good_pair == True:
        peer_review.belongs_to_good_pair = True
        junior_review.belongs_to_good_pair = True
    if belongs_to_good_pair == False:
        peer_review.belongs_to_good_pair = False
        junior_review.belongs_to_good_pair = False
    session = get_db_session()
    session.merge(peer_review)
    session.merge(junior_review)
    session.commit


def compute_item_result_score(item_id):
    reviews = get_good_reviews_by_item_id(item_id)
    average_scores = []
    for review in reviews:
        answers = get_review_answers_by_review_id_db(review.id)
        counter = 0
        answer_sum = 0
        for answer in answers:
            counter = counter + 1
            answer_sum = answer_sum + answer.answer
        answer_average = answer_sum / counter
        average_scores.append(answer_average)
    result = statistics.median(average_scores)
    return result

def get_open_items_for_user_db(user, num_items):
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

    session = get_db_session()

    sql_query_base = """SELECT items.id, min(submissions.submission_date) as oldest_submission,
                    reviews.id as review_id, SUM(IF(reviews.user_id = :user_id, 1,0)) AS reviewed_by_user
                    FROM items
                    INNER JOIN submissions ON items.id = submissions.item_id
                    LEFT JOIN reviews on items.id = reviews.item_id
                    WHERE {}
                    GROUP BY items.id
                    HAVING reviewed_by_user = 0
                    ORDER BY oldest_submission
                    LIMIT :num_items"""
    
    sql_query = sql_query_base.format("items.status = 'needs_junior'")

    # Senior detectives can get junior or senior reviews
    if user.level > 1:
        sql_query = sql_query_base.format("(items.status = 'needs_junior' OR items.status = 'needs_senior')")
    
    result = session.execute(sql_query, {"user_id": user.id, "num_items": num_items})
    print(result)

    items = []

    for row in result:
        item_id = row[0]
        item = get_item_by_id(item_id)
        items.append(item)

    # shuffle list order
    random.shuffle(items)

    return items


def get_url_by_content_db(content):
    """Returns an url with the specified content from the database

        Returns
        ------
        url: URL
            An url referenced in an item
        Null, if no url was found
        """
    session = get_db_session()
    url = session.query(URL).filter(URL.url == content).first()
    if url is None:
        raise Exception("No url found.")
    return url


def get_entity_by_content_db(content):
    """Returns an entity with the specified content from the database

        Returns
        ------
        entity: Entity
            An entity of an item
        Null, if no entity was found
        """
    session = get_db_session()
    entity = session.query(Entity).filter(Entity.entity == content).first()
    if entity is None:
        raise Exception("No entity found.")
    return entity


def get_organization_by_content_db(content):
    """Returns the organization publishing fact checks

        Returns
        ------
        org: FactChecking_Organization
        Null, if no org was found
        """
    session = get_db_session()
    org = session.query(FactChecking_Organization).filter(FactChecking_Organization.name == content).first()
    if org is None:
        raise Exception("No Organization found.")
    return org


def get_factcheck_by_url_and_item_db(factcheck_url, item_id):
    """Returns the factcheck publishing fact checks

        Returns
        ------
        factcheck: ExternalFactCheck
        Null, if no factcheck was found
        """
    session = get_db_session()
    factcheck = session.query(ExternalFactCheck).filter(ExternalFactCheck.url == factcheck_url,
                                                        ExternalFactCheck.item_id == item_id).first()
    if factcheck is None:
        raise Exception("No Factcheck found.")
    return factcheck


def get_itemurl_by_url_and_item_db(url_id, item_id):
    """Returns the itemurl for an item and url

        Returns
        ------
        itemurl: ItemURL
        Null, if no itemurl was found
        """
    session = get_db_session()
    itemurl = session.query(ItemURL).filter(ItemURL.url_id == url_id,
                                            ItemURL.item_id == item_id).first()
    if itemurl is None:
        raise Exception("No ItemURL found.")
    return itemurl


def get_itementity_by_entity_and_item_db(entity_id, item_id):
    """Returns the itementity for an item and entity

        Returns
        ------
        itementity: ItemEntity
        Null, if no itementity was found
    """
    session = get_db_session()
    itementity = session.query(ItemEntity).filter(ItemEntity.entity_id == entity_id,
                                            ItemEntity.item_id == item_id).first()
    if itementity is None:
        raise Exception("No ItemEntity found.")
    return itementity


def get_sentiment_by_content_db(content):
    """Returns the sentiment with the specified content from the database

        Returns
        ------
        sentiment: Sentiment
            The sentiment of an item
        Null, if no sentiment was found
        """
    session = get_db_session()
    sentiment = session.query(Sentiment).filter(Sentiment.sentiment == content).first()
    if sentiment is None:
        raise Exception("No sentiment found.")
    return sentiment


def get_itemsentiment_by_sentiment_and_item_db(sentiment_id, item_id):
    """Returns the itemsentiment for an item and sentiment

        Returns
        ------
        itemsentiment: ItemSentiment
        Null, if no itemsentiment was found
    """
    session = get_db_session()
    itemsentiment = session.query(ItemSentiment).filter(ItemSentiment.sentiment_id == sentiment_id,
                                            ItemSentiment.item_id == item_id).first()
    if itemsentiment is None:
        raise Exception("No Item Sentiment found.")
    return itemsentiment


def get_phrase_by_content_db(content):
    """Returns a keyphrase with the specified content from the database

        Returns
        ------
        keyphrase: Keyphrase
            A key phrase of an item
        Null, if no key phrase was found
        """
    session = get_db_session()
    phrase = session.query(Keyphrase).filter(Keyphrase.phrase == content).first()
    if phrase is None:
        raise Exception("No key phrase found.")
    return phrase


def get_itemphrase_by_phrase_and_item_db(phrase_id, item_id):
    """Returns the itemkeyphrase for an item and keyphrase

        Returns
        ------
        itemphrase: ItemKeyphrase
        Null, if no itemphrase was found
    """
    session = get_db_session()
    itemphrase = session.query(ItemKeyphrase).filter(ItemKeyphrase.keyphrase_id == phrase_id,
                                            ItemKeyphrase.item_id == item_id).first()
    if itemphrase is None:
        raise Exception("No ItemKeyphrase found.")
    return itemphrase


def reset_locked_items_db(items):
    """Updates all locked items in the database 
    and returns the amount of updated items"""
    counter = 0
    for item in items:
        if datetime.strptime(item.lock_timestamp, '%Y-%m-%d %H:%M:%S') < datetime.now() - timedelta(hours=1):
            counter = counter + 1
            item.lock_timestamp = None
            item.locked_by_user = None
            if item.status == "locked_by_junior":
                item.status = "needs_junior"
            if item.status == "locked_by_senior":
                item.status = "needs_senior"
            update_object_db(item)
    return counter

def accept_item_db(user, item):
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

    session = get_db_session()

    # The item cannot be reviewed if it is locked by a user
    if item.locked_by_user:
        raise ValueError('Item cannot be acceped since it is locked by user {}'.format(item.locked_by_user))

    # change status in order to lock item
    if item.status == "needs_junior":
        item.status = "locked_by_junior"
    else: 
        item.status = "locked_by_senior"
    
    item.lock_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    item.locked_by_user = user.id
    update_object_db(item)

    return item


def get_all_closed_items_db():
    """Gets all closed items

    Returns
    ------
    items: Item[]
        The closed items
    """

    session = get_db_session()

    items = session.query(Item).filter(Item.status == 'closed').all()
    return items