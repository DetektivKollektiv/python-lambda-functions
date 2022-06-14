import json
import pytest
from uuid import uuid4

from moto import mock_iotdata
from core_layer.boto_client_provider import BotoClientProvider


@pytest.fixture
def user_id_1():
    return str(uuid4())


@mock_iotdata
def test_pubsub_publish(user_id_1, monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:4200")
    monkeypatch.setenv("MOTO", "1")

    iot_client = BotoClientProvider().get_client('iot-data')

    message = "test_pubsub_publish-message"

    response = iot_client.publish(topic=user_id_1, payload=json.dumps({
        "message": message,
        "type": "level-up"
    }))

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
