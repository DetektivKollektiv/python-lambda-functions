import crud.operations as operations
from crud.model import ReviewInProgress, Item
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from datetime import datetime, timedelta


def test_reset_locked_items(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app
    session = operations.get_db_session(True, None)

    item = Item()
    item.content = "This item needs to be checked"
    item = operations.create_item_db(item, True, session)
    item.in_progress_reviews_level_2 = 2
    operations.update_object_db(item, True, session)

    items = operations.get_all_items_db(True, session)
    assert len(items) == 1

    rip1 = ReviewInProgress()
    rip1.id = "1"
    rip1.start_timestamp = datetime.now() + timedelta(hours=-2)
    rip1.item_id = item.id
    rip1.is_peer_review = True

    rip2 = ReviewInProgress()
    rip2.id = "2"
    rip2.start_timestamp = datetime.now()
    rip2.item_id = item.id
    rip2.is_peer_review = True

    session.add(rip1)
    session.add(rip2)
    session.commit()

    rips = session.query(ReviewInProgress).all()
    assert len(rips) == 2

    app.reset_locked_items(None, None, True, session)

    rips = session.query(ReviewInProgress).all()
    assert len(rips) == 1
    item = operations.get_item_by_id(item.id, True, session)
    assert item.in_progress_reviews_level_2 == 1
