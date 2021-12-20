

from core_layer.event_publisher import EventPublisher


def test_publish_event(monkeypatch):
    monkeypatch.setenv("STAGE", "test")

    event_publisher = EventPublisher()

    event_publisher.publish_event('test', 'test', {'test': 'test'})
