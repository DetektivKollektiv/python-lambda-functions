from core_layer.helper import set_cors
import pytest


@pytest.fixture
def set_deployment_mode(monkeypatch):
    monkeypatch.setattr('core_layer.helper.is_test', False)


def test_set_cors_header_no_origin(monkeypatch, mock_deployment):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:4200")
    event = {'headers': None}
    response = {}

    response = set_cors(response, event)


def test_set_cors_header_simple(monkeypatch, set_deployment_mode):

    origin = "http://localhost:4200"

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", origin)
    event = {'headers': {'Origin': origin}}
    response = {}

    response = set_cors(response, event)

    assert response['headers']['Access-Control-Allow-Origin'] == origin


def test_set_cors_header_non_capital(monkeypatch, set_deployment_mode):

    origin = "http://localhost:4200"

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", origin)
    event = {'headers': {'origin': origin}}
    response = {}

    response = set_cors(response, event)

    assert response['headers']['Access-Control-Allow-Origin'] == origin


def test_set_cors_header_multiple_allowed(monkeypatch, set_deployment_mode):

    origin = "http://localhost:4200"
    origin2 = "http://localhost:4201"

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", f'{origin},{origin2}')
    event = {'headers': {'origin': origin}}
    response = {}

    response = set_cors(response, event)

    assert response['headers']['Access-Control-Allow-Origin'] == origin

    event2 = {'headers': {'origin': origin2}}
    response2 = {}

    response2 = set_cors(response2, event2)

    assert response2['headers']['Access-Control-Allow-Origin'] == origin2


def test_set_cors_header_plugin(monkeypatch, set_deployment_mode):

    origin = "http://www.spiegel.de"
    monkeypatch.setenv("CORS_ALLOW_ORIGIN", '')

    event = {'headers': {'origin': origin}}

    response = set_cors({}, event, True)

    assert response['headers']['Access-Control-Allow-Origin'] == origin

    response2 = set_cors({}, event)
    assert 'headers' not in response2
