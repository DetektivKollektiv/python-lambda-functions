import json
from ... import attach_iot_policy

EVENT_EMPTY = {}

EVENT_USER_ID_NO_IDENTITY = {
    "requestContext": {
        "identity": {
            "cognitoAuthenticationProvider": "...CognitoSignIn:8b8fe3ad-1aba-420a-bb9a-3b13d524f726",
        }
    }
}

EVENT_IDENTITY_NO_USER_ID = {
    "requestContext": {
        "identity": {
            "cognitoIdentityId": "eu-central-1:de009839-c135-471d-ba70-98c9a050b4dd",
        }
    }
}

EVENT_USER_ID_IDENTITY = {
    "requestContext": {
        "identity": {
            "cognitoAuthenticationProvider": "...CognitoSignIn:8b8fe3ad-1aba-420a-bb9a-3b13d524f726",
            "cognitoIdentityId": "eu-central-1:de009839-c135-471d-ba70-98c9a050b4dd",
        }
    }
}


def test_empty_event(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:4200")

    response = attach_iot_policy.attach_iot_policy(EVENT_EMPTY, None)
    response_dict = json.loads(response)
    assert response_dict['statusCode'] == 400


def test_no_identity(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:4200")

    response = attach_iot_policy.attach_iot_policy(
        EVENT_USER_ID_NO_IDENTITY, None)
    response_dict = json.loads(response)
    assert response_dict['statusCode'] == 400


def test_no_user_id(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:4200")

    response = attach_iot_policy.attach_iot_policy(
        EVENT_IDENTITY_NO_USER_ID, None)
    response_dict = json.loads(response)
    assert response_dict['statusCode'] == 400
