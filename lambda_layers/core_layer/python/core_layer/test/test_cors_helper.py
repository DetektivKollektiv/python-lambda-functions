from core_layer.helper import set_cors


def test_set_cors_header_no_origin(monkeypatch):

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:4200")
    event = {'headers': None}
    response = {}

    response = set_cors(response, event)


def test_set_cors_header_simple(monkeypatch):

    origin = "http://localhost:4200"

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", origin)
    event = {'headers': {'Origin': origin}}
    response = {}

    response = set_cors(response, event)

    assert response['headers']['Access-Control-Allow-Origin'] == origin


def test_set_cors_header_non_capital(monkeypatch):

    origin = "http://localhost:4200"

    monkeypatch.setenv("CORS_ALLOW_ORIGIN", origin)
    event = {'headers': {'origin': origin}}
    response = {}

    response = set_cors(response, event)

    assert response['headers']['Access-Control-Allow-Origin'] == origin


def test_set_cors_header_multiple_allowed(monkeypatch):

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
