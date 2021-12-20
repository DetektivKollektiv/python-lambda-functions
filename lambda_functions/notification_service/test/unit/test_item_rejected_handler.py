import json

from notification_service.src import item_rejected_handler


def test_no_item_id(monkeypatch):
    event = {}

    response = item_rejected_handler.handle_item_rejected(event, None)
    response_dict = json.loads(response)
    assert response_dict['statusCode'] == 400


def test_wrong_item_id(monkeypatch):
    event = {"detail": {"item_id": "e9e376b5-0444-4eff-a7af-a3189ba2291e"}}

    response = item_rejected_handler.handle_item_rejected(event, None)
    response_dict = json.loads(response)
    assert response_dict['statusCode'] == 400
