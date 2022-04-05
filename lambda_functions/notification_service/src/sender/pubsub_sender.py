import logging
from botocore.exceptions import ClientError
from core_layer.handler.notification_template_handler import S3NotificationTemplateHandler
from core_layer.boto_client_provider import BotoClientProvider
from .notification_sender import NotificationSender

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PubsubSender(NotificationSender):

    def __init__(self, notification_template_handler: S3NotificationTemplateHandler) -> None:
        super().__init__(notification_template_handler)

        self._message_type = "pubsub"

    def pubsub_publish(user_id, message):
        iot_client = BotoClientProvider().get_client('iot-data')

        response = iot_client.publish(topic=user_id, payload={
            "message": message,
            "type": "level_up"
        })
