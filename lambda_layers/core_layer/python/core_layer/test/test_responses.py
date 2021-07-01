import pytest

from core_layer.responses import BadRequest, Created, InternalError, NoContent, ResponseBase, Success

ORIGIN = "http://localhost:4711"
ORIGIN2 = "http://localhost:4712"
ORIGINS = f'{ORIGIN},{ORIGIN2}'


def test_response_base_single_origin(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    event = {
        'headers': {
            'origin': ORIGIN
        }
    }

    response = ResponseBase(event)

    assert response.headers['Access-Control-Allow-Origin'] == ORIGIN


def test_response_base_multiple_origins(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGINS)

    event = {
        'headers': {
            'origin': ORIGIN
        }
    }

    response = ResponseBase(event)

    print(response)

    assert response.headers['Access-Control-Allow-Origin'] == ORIGIN


def test_response_base_no_source_origins(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    event = {
        'headers': {

        }
    }

    response = ResponseBase(event)

    print(response)

    assert 'Access-Control-Allow-Origin' not in response.headers


def test_response_base_different_source_origins(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    event = {
        'headers': {
            'origin': ORIGIN2
        }
    }

    response = ResponseBase(event)

    assert 'Access-Control-Allow-Origin' not in response.headers


def test_response_base_no_allowed_origins():
    with pytest.raises(KeyError):
        ResponseBase({})


def test_internal_error(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    response = InternalError({})

    assert response.statusCode == 500
    assert response.body == "An unexpected error occured."


def test_internal_error_message(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    MESSAGE = "message"
    response = InternalError({}, message=MESSAGE)

    assert response.statusCode == 500
    assert response.body is not None
    assert response.body == MESSAGE


def test_internal_error_exception(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    response = InternalError({}, exception=KeyError())

    assert response.statusCode == 500
    assert response.body is not None
    assert isinstance(response.body, KeyError)


def test_internal_error_message_and_exception(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    MESSAGE = "message"
    response = InternalError({}, message=MESSAGE, exception=KeyError())

    assert response.statusCode == 500
    assert response.body is not None
    assert response.body['message'] == MESSAGE
    assert isinstance(response.body['exception'], KeyError)


def test_bad_request(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    response = BadRequest({})

    assert response.statusCode == 400
    assert response.body is None


def test_bad_request_with_message(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)
    MESSAGE = "message"
    response = BadRequest({}, MESSAGE)

    assert response.statusCode == 400
    assert response.body is not None
    assert response.body == MESSAGE


def test_success(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    response = Success({})

    assert response.statusCode == 200
    assert response.body is None


def test_no_content(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    response = NoContent({})

    assert response.statusCode == 204
    assert response.body is None


def test_bad_request(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", ORIGIN)

    response = Created({})

    assert response.statusCode == 201
    assert response.body is None
