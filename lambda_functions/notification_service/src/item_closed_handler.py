import logging
import os

from core_layer import helper
from core_layer.handler.notification_template_handler import S3NotificationTemplateHandler
from core_layer.responses import BadRequest, InternalError, Success
from core_layer.handler import item_handler
from notification_service.src.sender.mail_sender import MailSender
from notification_service.src.sender.telegram_sender import TelegramSender


logger = logging.getLogger()
logger.setLevel(logging.INFO)

notification_template_handler = S3NotificationTemplateHandler()

mail_sender = MailSender(notification_template_handler)
telegram_sender = TelegramSender(notification_template_handler)


def handle_item_closed(event, context):
    try:
        stage = os.getenv("STAGE")
        is_test = stage is not None and stage == "test"

        session = helper.get_db_session(is_test, None)

        helper.log_method_initiated("Send notification", event, logger)

        if "item_id" not in event:
            return BadRequest(event, "Event contains no item_id.")

        item_id = event["item_id"]
        item = item_handler.get_item_by_id(item_id, is_test, session)

        if item is None:
            return BadRequest(event,
                              f"No item was found with the given item_id [{item_id}].")

        # TODO: This implementation is not ideal: 1.55 is rounded to 1.5. However, 1.56 is correctly rounded to 1.6.
        rating = round(item.result_score, 1)
        rating_text = get_rating_text(rating)

        parameters = dict(
            rating=rating, rating_text=rating_text, item_id=item.id, content=item.content
        )

        for submission in item.submissions:
            if submission.mail is not None:
                try:
                    mail_sender.send_notification(
                        "item_closed", mail=submission.mail, replacements=parameters)
                except Exception as e:
                    logger.exception(e)

            if submission.telegram_id is not None:
                try:
                    mail_sender.send_notification(
                        "item_closed", telegram_id=submission.telegram_id, replacements=parameters)
                except Exception as e:
                    logger.exception(e)

        return Success(event)

    except Exception as e:
        return InternalError(event, "Error sending notification", e)


def get_rating_text(rating: float) -> str:
    if 2 <= rating < 3:
        return "eher nicht vertrauenswürdig"
    elif 3 <= rating < 3.5:
        return "eher vertrauenswürdig"
    elif rating >= 3.5:
        return "vertrauenswürdig"
    else:
        return "nicht vertrauenswürdig"