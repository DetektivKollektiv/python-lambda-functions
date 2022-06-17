import pytest

from core_layer.sender.notification_sender import NotificationSender

from notification_service.tests.mocks.mock_notification_template_handler import MockNotificationTemplateHandler

TEST_STRING = "Dein Fall {placeholder1} wurde gelöst! {placeholder2}"
TEST_STRING_ONE_PLACEHOLDER = "Dein Fall {placeholder1} wurde gelöst!"
TEST_STRING_TWO_PLACEHOLDERS = "Dein Fall {placeholder1} wurde gelöst! {placeholder2}"


REPLACED_STRING_ONE_PLACEHOLDER = "Dein Fall 1 wurde gelöst!"
REPLACED_STRING_TWO_PLACEHOLDERS = "Dein Fall 1 wurde gelöst! 2"

tempalte_handler = MockNotificationTemplateHandler()


def test_no_replacements():
    notification_sender = NotificationSender(tempalte_handler)

    replaced = notification_sender._replace_placeholders(TEST_STRING)

    assert replaced == TEST_STRING


def test_one_replacement():
    notification_sender = NotificationSender(tempalte_handler)
    replacements = dict(placeholder1=1)

    replaced = notification_sender._replace_placeholders(
        TEST_STRING_ONE_PLACEHOLDER, replacements
    )

    assert replaced != TEST_STRING
    assert replaced == REPLACED_STRING_ONE_PLACEHOLDER


def test_many_replacement():
    notification_sender = NotificationSender(tempalte_handler)
    replacements = dict(
        placeholder1=1,
        placeholder2=2,
    )

    replaced = notification_sender._replace_placeholders(
        TEST_STRING_TWO_PLACEHOLDERS, replacements
    )

    assert replaced != TEST_STRING
    assert replaced == REPLACED_STRING_TWO_PLACEHOLDERS


def test_additional_replacement():
    notification_sender = NotificationSender(tempalte_handler)
    replacements = dict(
        placeholder1=1,
        placeholder2=2,
        placeholder3=3,
    )

    replaced = notification_sender._replace_placeholders(
        TEST_STRING_TWO_PLACEHOLDERS, replacements
    )

    assert replaced != TEST_STRING
    assert replaced == REPLACED_STRING_TWO_PLACEHOLDERS


def test_missing_replacement():
    notification_sender = NotificationSender(tempalte_handler)
    replacements = dict(
        placeholder1=1,
    )

    with pytest.raises(KeyError):
        notification_sender._replace_placeholders(
            TEST_STRING_TWO_PLACEHOLDERS, replacements
        )
