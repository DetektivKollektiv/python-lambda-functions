import logging
import json

from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler.notification_template_handler import S3NotificationTemplateHandler
from core_layer.responses import BadRequest, InternalError, Success
from core_layer.handler import item_handler
from .sender.mail_sender import MailSender
from .sender.telegram_sender import TelegramSender


logger = logging.getLogger()
logger.setLevel(logging.INFO)

notification_template_handler = S3NotificationTemplateHandler()

mail_sender = MailSender(notification_template_handler)
telegram_sender = TelegramSender(notification_template_handler)


def handle_item_rejected(event, context):
    try:
        with Session() as session:
            helper.log_method_initiated("Handle item rejected", event, logger)

            if "item_id" not in event:
                return BadRequest(event, "Event contains no item_id.", add_cors_headers=False).to_json_string()

            item_id = event["item_id"]
            item = item_handler.get_item_by_id(item_id, session)

            if item is None:
                return BadRequest(event, f"No item was found with the given item_id [{item_id}].", add_cors_headers=False).to_json_string()

            parameters = dict(
                content=item.content
            )

            for submission in item.submissions:
                if submission.mail is not None:
                    try:
                        mail_sender.send_notification(
                            "item_rejected", mail=submission.mail, replacements=parameters)
                    except Exception as e:
                        logger.exception(e)

                if submission.telegram_id is not None:
                    try:
                        mail_sender.send_notification(
                            "item_rejected", telegram_id=submission.telegram_id, replacements=parameters)
                    except Exception as e:
                        logger.exception(e)

            return Success(event, add_cors_headers=False).to_json_string()
    except Exception as e:
        return InternalError(event, "Error sending notification", e, add_cors_headers=False).to_json_string()
