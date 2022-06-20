
from core_layer.db_handler import clear_database, init_database
import pytest


@pytest.fixture(autouse=True)
def database_fixture():
    init_database()
    yield
    clear_database()