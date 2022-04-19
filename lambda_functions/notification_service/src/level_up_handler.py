import logging

from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from core_layer.responses import BadRequest, InternalError
from notification_service.src.sender.pubsub_sender import PubsubSender


logger = logging.getLogger()
logger.setLevel(logging.INFO)

notification_template_handler = NotificationTemplateHandler()

pubsub_sender = PubsubSender(notification_template_handler)


def handle_level_up(event, context):
    try:
        helper.log_method_initiated(
            "Send pubsub notification: levelup", event, logger)

        if "Detail" not in event or "user_id" not in event["Detail"]:
            return BadRequest(event, "Event contains no user_id", add_cors_headers=False).to_json_string()

        user_id = event["Detail"]["user_id"]

        pubsub_sender.send_notification("level_up", user_id)

    except Exception as e:
        return InternalError(event, "Error sending pubsub notification: levelup", e, add_cors_headers=False).to_json_string()
