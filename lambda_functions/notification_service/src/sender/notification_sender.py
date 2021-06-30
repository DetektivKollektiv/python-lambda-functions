import logging

from core_layer.boto_client_provider import BotoClientProvider
from core_layer.handler.notification_template_handler import S3NotificationTemplateHandler


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class NotificationSender:

    _notification_type: str
    _message_type: str

    _client_provider: BotoClientProvider
    _notification_template_handler: S3NotificationTemplateHandler

    def __init__(self, notification_template_handler: S3NotificationTemplateHandler) -> None:
        self._client_provider = BotoClientProvider()
        self._notification_template_handler = notification_template_handler
        pass

    def _send_notification_internal(self, **kwargs):
        raise NotImplementedError()

    def _get_text(self, text_type: str, replacements) -> str:

        notification_template = self._notification_template_handler.get_notification_template(
            self._notification_type, self._message_type, text_type, "de")

        return self._replace_placeholders(notification_template.content, replacements)

    def _replace_placeholders(self, input: str, replacements: dict = None) -> str:
        if(input is None):
            raise Exception

        if(replacements is None):
            return input

        return input.format(**replacements)

    def send_notification(
        self, topic: str, **kwargs
    ):
        """Sends a notification of the provided topic via the provided notification_type.

        Parameters
        ----------
        notification_type: string
            The type of notification to send (mail, telegram, ...)

        topic: string
            The topic of the notification (must be present in the message_templates)

        """
        self._notification_type = topic

        self._send_notification_internal(**kwargs)
