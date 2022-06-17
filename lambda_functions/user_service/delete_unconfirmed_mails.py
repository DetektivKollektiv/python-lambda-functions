import logging
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import user_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def delete_unconfirmed_mails(event, context):

    helper.log_method_initiated("Delete unconfirmed mails", event, logger)

    with Session() as session:

        try:
            counter = user_handler.delete_unconfirmed_mails(session)
            logger.info("Deleted {} unconfirmed mails.".format(counter))
            return
        except Exception:
            logger.error("Error while deleting unconfirmed mails.")
            return