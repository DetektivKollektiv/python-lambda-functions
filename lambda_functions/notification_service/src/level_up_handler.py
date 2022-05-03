import logging
import core_layer.handler.user_handler

from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from core_layer.model.user_model import User
from core_layer.responses import BadRequest, InternalError, Success
from core_layer.sender.pubsub_sender import PubsubSender


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

        with Session() as session:
            user_id = event["Detail"]["user_id"]

            user: User = core_layer.handler.user_handler.get_user_by_id(
                session, user_id)
            if user is None:
                return BadRequest(event,
                                  f"No user was found with the given item_id [{user_id}].", add_cors_headers=False).to_json_string()

            user_name = user.name
            user_level = user.level_id

            parameters: dict(
                name=user_name,
                level=user_level
            )

            try:
                pubsub_sender.send_notification(
                    "level_up", user_id, parameters)
            except Exception as exception:
                logger.exception(exception)

        return Success(event, add_cors_headers=False).to_json_string()

    except Exception as e:
        return InternalError(event, "Error sending pubsub notification: levelup", e, add_cors_headers=False).to_json_string()
