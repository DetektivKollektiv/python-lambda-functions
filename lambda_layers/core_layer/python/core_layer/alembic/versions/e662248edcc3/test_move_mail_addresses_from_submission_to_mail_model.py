import pytest
from core_layer.alembic.versions.e662248edcc3.move_mail_addresses_from_submission_to_mail_model import move_mail_addresses_from_submission_to_mail_model

from core_layer.test.helper.fixtures import database_fixture

def test(monkeypatch, database_fixture):
    monkeypatch.setenv("STAGE", "dev")
    move_mail_addresses_from_submission_to_mail_model()
    assert 1 == 1