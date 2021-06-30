import logging
import os

from core_layer import helper
from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from core_layer.responses import BadRequest, InternalError, Success
from core_layer.handler import item_handler
from notification_service.src.sender.mail_sender import MailSender
from notification_service.src.sender.telegram_sender import TelegramSender


logger = logging.getLogger()
logger.setLevel(logging.INFO)

notification_template_handler = NotificationTemplateHandler()

mail_sender = MailSender(notification_template_handler)
telegram_sender = TelegramSender(notification_template_handler)


def handle_item_rejected(event, context):
    try:
        stage = os.getenv("STAGE")
        is_test = stage is not None and stage == "test"

        session = helper.get_db_session(is_test, None)

        helper.log_method_initiated("Handle item rejected", event, logger)

        if "item_id" not in event:
            response = BadRequest("Event contains no item_id.")
            return helper.set_cors(response, event, is_test)

        item_id = event["item_id"]
        item = item_handler.get_item_by_id(item_id, is_test, session)

        if item is None:
            response = BadRequest(
                f"No item was found with the given item_id [{item_id}].")
            return helper.set_cors(response, event, is_test)

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

        response = Success()
        return helper.set_cors(response, event, is_test)
    except Exception as e:
        response = InternalError("Error sending notification", e)
        return helper.set_cors(response, event, is_test)
