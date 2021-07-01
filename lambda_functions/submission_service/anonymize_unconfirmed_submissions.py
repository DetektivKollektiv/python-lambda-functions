import logging
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import submission_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def anonymize_unconfirmed_submissions(event, context):

    helper.log_method_initiated("Anonymize unconfirmed submissions", event, logger)

    with Session() as session:

        try:
            counter = submission_handler.anonymize_unconfirmed_submissions(session)
            logger.info("Anonymized {} submissions.".format(counter))
            return
        except Exception:
            logger.error("Error while anonymizing submissions.")
            return
