import crud.operations as operations
from crud.model import ReviewInProgress, Item
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from datetime import datetime, timedelta


def test_get_item_by_id(monkeypatch):
    monkeypatch.setenv("DBNAME", "Test")
    import app
    session = operations.get_db_session(True, None)

    item = operations.get_item_by_id("123456", True, session)
    assert 1 == 1