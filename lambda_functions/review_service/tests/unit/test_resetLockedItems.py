import pytest
# import json
from sqlalchemy.orm import Session
from core_layer.connection_handler import get_db_session, update_object

from core_layer.model.review_model import Review
from core_layer.model.item_model import Item

from core_layer.handler import user_handler, item_handler
from core_layer import helper

from datetime import datetime, timedelta
from ...reset_locked_items import reset_locked_items


def test_reset_locked_items(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    session = get_db_session(True, None)

    item = Item()
    item.content = "This item needs to be checked"
    item = item_handler.create_item(item, True, session)
    item.in_progress_reviews_level_2 = 2
    update_object(item, True, session)

    items = item_handler.get_all_items(True, session)
    assert len(items) == 1

    rip1 = Review()
    rip1.id = "1"
    rip1.start_timestamp = datetime.now() + timedelta(hours=-2)
    rip1.item_id = item.id
    rip1.is_peer_review = True
    rip1.status = "in_progress"

    rip2 = Review()
    rip2.id = "2"
    rip2.start_timestamp = datetime.now()
    rip2.item_id = item.id
    rip2.is_peer_review = True
    rip1.status = "in_progress"

    session.add(rip1)
    session.add(rip2)
    session.commit()

    rips = session.query(Review).all()
    assert len(rips) == 2

    reset_locked_items(None, None, True, session)

    rips = session.query(Review).all()
    assert len(rips) == 1
    item = item_handler.get_item_by_id(item.id, True, session)
    assert item.in_progress_reviews_level_2 == 1
