import boto3
import logging
from botocore.exceptions import ClientError, ParamValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client(service_name='comprehend', region_name='eu-central-1')


def get_language(event, context):
    """ Detect Dominant Language in Item Text
    returns only the most dominant language code
    other language codes and scores are dropped
    Parameters
    ----------
    event: dict, required
        "Text": item content
    context: object, optional
        Lambda Context runtime methods and attributes
    Returns
    ------
    LanguageCode, supported language codes are ['en', 'es', 'fr', 'de', 'it', 'pt', 'ar', 'hi', 'ja', 'ko', 'zh', 'zh-TW']
    """
    logger.info('Calling get_language with event')
    logger.info(event)

    # Use UTF-8 encoding for comprehend
    if 'Text' in event:
        text = str(event['Text'])
    else:
        logger.error("There is no Text!")
        raise Exception('Please provide Text!')

    # comprehend accepts up to 5000 UTF-8 encoded characters
    if len(text) >= 4900:
        text = text[:4899]
    elif len(text) < 20:
        logger.warning("Text is shorter than 20 characters!")
        raise Exception('Please provide a text of at least 20 characters!')
    # logger.info(text)

    try:
        response = comprehend.detect_dominant_language(Text=text)
    except ClientError as e:
        logger.error("Received error: %s", e, exc_info=True)
        raise
    except ParamValidationError as e:
        logger.error("The provided parameters are incorrect: %s", e, exc_info=True)
        raise

    # logger.info(response)
    return response['Languages'][0]['LanguageCode']
