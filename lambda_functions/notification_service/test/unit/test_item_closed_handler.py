import pytest
import json

from notification_service.src import item_closed_handler


def test_no_item_id(monkeypatch):
    event = {}

    response = item_closed_handler.handle_item_closed(event, None)
    response_dict = json.loads(response)
    assert response_dict['statusCode'] == 400


def test_wrong_item_id(monkeypatch):
    event = {"item_id": "123123"}

    response = item_closed_handler.handle_item_closed(event, None)
    response_dict = json.loads(response)
    assert response_dict['statusCode'] == 400


testdata = [
    (1, "nicht vertrauenswürdig"),
    (2, "eher nicht vertrauenswürdig"),
    (3, "eher vertrauenswürdig"),
    (4, "vertrauenswürdig")
]


@pytest.mark.parametrize("input, expected", testdata)
def test_get_rating_text(input: float, expected: str):

    rating_text = item_closed_handler.get_rating_text(input)

    assert rating_text == expected