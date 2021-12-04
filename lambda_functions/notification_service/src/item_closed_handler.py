import logging

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


def handle_item_closed(event, context):
    try:
        helper.log_method_initiated("Send notification", event, logger)

        if "detail" not in event or "item_id" not in event["detail"]:
            return BadRequest(event, "Event contains no item_id.", add_cors_headers=False).to_json_string()

        with Session() as session:
            item_id = event["detail"]["item_id"]
            item = item_handler.get_item_by_id(item_id, session)

            if item is None:
                return BadRequest(event,
                                  f"No item was found with the given item_id [{item_id}].", add_cors_headers=False).to_json_string()

            rating = int(item.result_score * 25)
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

            return Success(event, add_cors_headers=False).to_json_string()

    except Exception as e:
        return InternalError(event, "Error sending notification", e, add_cors_headers=False).to_json_string()


def get_rating_text(rating: int) -> str:
    if 34 <= rating < 67:
        return "eher nicht vertrauenswürdig"
    elif 67 <= rating < 84:
        return "eher vertrauenswürdig"
    elif rating >= 84:
        return "vertrauenswürdig"
    else:
        return "nicht vertrauenswürdig"
