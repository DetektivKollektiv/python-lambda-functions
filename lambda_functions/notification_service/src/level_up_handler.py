import logging

from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler.notification_template_handler import S3NotificationTemplateHandler
from core_layer.responses import BadRequest, InternalError, Success
from core_layer.handler import item_handler
from notification_service.src.sender.pubsub_sender import PubsubSender
from .sender.mail_sender import MailSender
from .sender.telegram_sender import TelegramSender


logger = logging.getLogger()
logger.setLevel(logging.INFO)

notification_template_handler = S3NotificationTemplateHandler()

pubsub_sender = PubsubSender(notification_template_handler)


def handle_level_up(event, context):
    try:
        helper.log_method_initiated(
            "Send pubsub notification: levelup", event, logger)

        user_id = event["Detail"]["user_id"]

        message = "Herzlichen Glückwunsch, du bist ein Level aufgestiegen!"

        pubsub_sender.pubsub_publish(user_id, message)

    except Exception as e:
        return InternalError(event, "Error sending pubsub notification: levelup", e, add_cors_headers=False).to_json_string()
