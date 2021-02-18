import logging
import traceback
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import submission_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def anonymize_unconfirmed_submissions(event, context, is_test=False, session=None):

    helper.log_method_initiated(
        "Anonymize unconfirmed submissions", event, logger)

    if session == None:
        session = get_db_session(False, None)

    try:
        counter = submission_handler.anonymize_unconfirmed_submissions(
            is_test, session)
        logger.info("Anonymized {} submissions.".format(counter))
        return
    except Exception:
        logger.error("Error while anonymizing submissions.")
        return
