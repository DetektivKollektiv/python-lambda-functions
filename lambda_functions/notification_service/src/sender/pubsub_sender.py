import logging

from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from botocore.exceptions import ClientError
from core_layer.sender.notification_sender import NotificationSender

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PubsubSender(NotificationSender):
    def __init__(self, notification_template_handler: NotificationTemplateHandler) -> None:
        super().__init__(notification_template_handler)

        self._message_type = "pubsub"

    def _send_notification_internal(self, user_id, replacements: dict = None):
        """Notifies a user in frontend via user_id.

        Parameters
        ----------
        user_id: string
            The users' user id

        replacements: dict (optional)
            Dictionary of replacements that should be replaced in the notification message and subject.
            Key: The placeholder in the message and subject
            Value: The value to replace the placeholder with

        """

        AWS_REGION = "eu-central-1"
        message = self._get_text("text", replacements)
        notification_type = self._notification_type

        client = self._client_provider.get_client("iot-data", AWS_REGION)

        try:
            response = client.publish(topic=user_id, payload={
                "message": message,
                "type": notification_type
            })
            logger.info(
                f"Notification sent via pubsub to user: {user_id}. Message-type: {notification_type}")
        except ClientError as e:
            logging.exception(
                f"Could not send message to user: {user_id}. Message-type: {notification_type}. Error: {e.response['Error']['Message']}")
            raise Exception

        pass
