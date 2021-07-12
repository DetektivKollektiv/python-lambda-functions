import os

from notification_service.src.sender.mail_sender import MailSender

from notification_service.test.mocks.mock_notification_template_handler import MockNotificationTemplateHandler

# awslocal ses verify-email-identity --email-address no-reply@codetekt.org


def test():

    template_handler = MockNotificationTemplateHandler()
    mail_sender = MailSender(template_handler)

    mail_sender.send_notification("test1", mail="test@test.com")

    assert 1 == 1
