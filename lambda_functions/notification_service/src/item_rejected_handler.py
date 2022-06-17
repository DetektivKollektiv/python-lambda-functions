import logging
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from core_layer.responses import BadRequest, InternalError, Success
from core_layer.handler import item_handler, mail_handler
from core_layer.sender.mail_sender import MailSender
from core_layer.sender.telegram_sender import TelegramSender


logger = logging.getLogger()
logger.setLevel(logging.INFO)

notification_template_handler = NotificationTemplateHandler()

mail_sender = MailSender(notification_template_handler)
telegram_sender = TelegramSender(notification_template_handler)


def handle_item_rejected(event, context):
    try:
        helper.log_method_initiated("Handle item rejected", event, logger)

        if "detail" not in event or "item_id" not in event["detail"]:
            return BadRequest(event, "Event contains no item_id.", add_cors_headers=False).to_json_string()

        with Session() as session:

            item_id = event["detail"]["item_id"]
            item = item_handler.get_item_by_id(item_id, session)

            if item is None:
                return BadRequest(event, f"No item was found with the given item_id [{item_id}].", add_cors_headers=False).to_json_string()

            parameters = dict(
                content=item.content
            )

            for submission in item.submissions:
                if submission.mail is not None:
                    parameters['mail_unsubscribe_link'] = mail_handler.get_unsubscribe_link(submission.mail.id)                    
                    try:
                        mail_sender.send_notification(
                            "item_rejected", mail=submission.mail.email, replacements=parameters)
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
        response = InternalError(
            event, "Error sending notification", e, add_cors_headers=False).to_json_string()
        logger.error(response)

        return response
