import pytest
from core_layer.alembic.versions.f090daf85005.calculate_warning_tags import calculate_warning_tags

from core_layer.test.helper.fixtures import database_fixture

def test(database_fixture):
    calculate_warning_tags()
    assert 1 == 1
