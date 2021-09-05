import os
import pytest

from notification_service.src.sender.notification_sender import NotificationSender

from notification_service.tests.mocks.mock_notification_template_handler import MockNotificationTemplateHandler


this_file = os.path.dirname(__file__)


template_handler = MockNotificationTemplateHandler()


def mock_file(*args, **kwargs):
    return this_file


def test_random_type_and_topic():
    notification_sender = NotificationSender(template_handler)

    with pytest.raises(Exception):
        notification_sender.send_notification("OgFe4hXZ1R", "b5WTitEjEA")


def test_random_type(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", mock_file)

    notification_sender = NotificationSender(template_handler)

    with pytest.raises(Exception):
        notification_sender.send_notification("b5WTitEjEA", "test1")


def test_existing_entry(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", mock_file)

    notification_sender = NotificationSender(template_handler)

    notification_sender._notification_type = "mail"

    with pytest.raises(NotImplementedError):
        notification_sender.send_notification(
            "test1", mail="sandro.glueck@gmail.com"
        )
