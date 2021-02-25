import pytest
from uuid import uuid4
from sqlalchemy.orm import Session, sessionmaker

from core_layer.model.review_model import Review
from core_layer.model.item_model import Item

import pytest
from core_layer.handler import user_handler, item_handler
from core_layer import helper

from datetime import datetime, timedelta
from ...reset_locked_items import reset_locked_items

from core_layer.model import Review
from core_layer.model import ReviewPair
from core_layer.model import Item

from core_layer.connection_handler import get_db_session, update_object


@pytest.fixture
def item():
    item = Item()
    item.id = str(uuid4())
    item.in_progress_reviews_level_1 = 1
    item.in_progress_reviews_level_2 = 1
    return item


@pytest.fixture
def old_junior_review(item):
    rip1 = Review()
    rip1.id = str(uuid4())
    rip1.start_timestamp = datetime.now() + timedelta(hours=-2)
    rip1.is_peer_review = False
    rip1.status = "in_progress"
    rip1.item_id = item.id
    return rip1


@pytest.fixture
def new_senior_review(item):
    rip2 = Review()
    rip2.id = str(uuid4())
    rip2.start_timestamp = datetime.now()
    rip2.is_peer_review = True
    rip2.status = "in_progress"
    rip2.item_id = item.id
    return rip2


@pytest.fixture
def pair(old_junior_review, new_senior_review):
    pair = ReviewPair()
    pair.id = str(uuid4())
    pair.junior_review_id = old_junior_review.id
    pair.senior_review_id = new_senior_review.id
    return pair


@pytest.fixture
def session(item, pair, old_junior_review, new_senior_review):
    session = get_db_session(True, None)
    session.add(item)
    session.add(old_junior_review)
    session.add(new_senior_review)
    session.add(pair)
    session.commit()

    return session


def test_reset_locked_items(session, item, pair, old_junior_review, new_senior_review):

    rips = session.query(Review).all()
    assert len(rips) == 2

    response = reset_locked_items(None, None, True, session)
    assert response['statusCode'] == 200
    assert "1" in response['body']

    rips = session.query(Review).all()
    assert len(rips) == 1
    item = item_handler.get_item_by_id(item.id, True, session)
    assert item.in_progress_reviews_level_2 == 1
    assert item.in_progress_reviews_level_1 == 0

    session.refresh(pair)
    assert pair.junior_review_id == None
    assert pair.senior_review_id == new_senior_review.id
