

from core_layer.handler.notification_template_handler import S3NotificationTemplateHandler


def test_s3_handler(monkeypatch):
    monkeypatch.setenv("STAGE", "dev")
    monkeypatch.setenv("NOTIFICATION_TEMPLATE_BUCKET",
                       "codetekt-notification-templates-dev")

    template = S3NotificationTemplateHandler().get_notification_template(
        "item_closed", "mail", "html")

    assert template.content is not None
