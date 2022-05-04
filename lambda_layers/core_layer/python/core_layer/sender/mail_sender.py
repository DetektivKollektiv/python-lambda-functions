import logging

from botocore.exceptions import ClientError
from core_layer.handler.notification_template_handler import NotificationTemplateHandler

from .notification_sender import NotificationSender

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MailSender(NotificationSender):
    def __init__(self, notification_template_handler: NotificationTemplateHandler) -> None:
        super().__init__(notification_template_handler)

        self._message_type = "mail"

    def _send_notification_internal(self, mail: str, replacements: dict = None):
        """Notifies a telegram user via their telegram_id (= chat_id).

        Parameters
        ----------
        mail: string
            The user's mail address

        replacements: dict (optional)
            Dictionary of replacements that should be replaced in the notification message and subject.
            Key: The placeholder in the message and subject
            Value: The value to replace the placeholder with

        """

        subject = self._get_text('subject', replacements)
        text = self._get_text('text', replacements)
        html = self._get_text('html', replacements)

        SENDER = "codetekt <no-reply@codetekt.org>"

        # The region the desired SES service is located in
        AWS_REGION = "eu-central-1"

        # The character encoding for the email.
        CHARSET = "UTF-8"

        RECIPIENT = mail

        # The subject line for the email
        SUBJECT = subject

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = text

        # The HTML body of the email
        BODY_HTML = html

        client = self._client_provider.get_client('ses', AWS_REGION)

        # Try to send the email.
        try:
            # Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                    'BccAddresses': [
                        'support@codetekt.org',
                    ]
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )
            logger.info(
                f"Notification email sent to {RECIPIENT}. SES Message ID: {response['MessageId']}")
        except ClientError as e:
            logging.exception(
                f"Could not send mail notification to email address {RECIPIENT}. SNS Error: {e.response['Error']['Message']}")
            raise Exception

        pass
