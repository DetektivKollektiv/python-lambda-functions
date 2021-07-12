import os

from core_layer.boto_client_provider import BotoClientProvider


class NotificationTemplate:
    message_type: str
    content_type: str
    language: str
    content: str


class NotificationTemplateHandlerBase:
    def _get_notification_template(self, notification_type: str, message_type: str, content_type: str, language: str):
        raise NotImplementedError()

    def get_notification_template(self, notification_type: str, message_type: str, content_type: str, language: str = "de") -> NotificationTemplate:
        """ Returns a notification template based on a given notification_type and a content_type

            Parameters
            ------
            notification_type: str
                The type of notification (item_closed, item_rejected, ...)

            message_type: str
                The type of message to send (mail, telegram, ...)

            content_type: str
                The type of content (html, text, subject, ...)

            Returns
            ------
            template: NotificationTemplate
                Null, if no entity was found
        """

        return self._get_notification_template(notification_type, message_type, content_type, language)


class S3NotificationTemplateHandler(NotificationTemplateHandlerBase):
    def _get_notification_template(self, notification_type: str, message_type: str, content_type: str, language: str):
        client = BotoClientProvider().get_client("s3")

        response = client.get_object(
            # 'codetekt-notification-templates-dev',
            Bucket=os.environ['NOTIFICATION_TEMPLATE_BUCKET'],
            Key=f'{message_type}/{language}/{notification_type}/{content_type}.txt'
        )

        template = NotificationTemplate()

        template.message_type = message_type
        template.content_type = content_type
        template.language = language
        template.content = response['Body'].read().decode("utf-8")

        return template
