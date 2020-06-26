import boto3
import logging
from botocore.exceptions import ClientError, ParamValidationError
from operator import itemgetter

supportedLanguageCodes = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ar', 'hi', 'ja', 'ko', 'zh', 'zh-TW']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client(service_name='comprehend', region_name='eu-central-1')


# Detect Sentiment
def get_sentiment(event, context):
    """detect sentiment of item content
    Parameters
    ----------
    event: dict, required
        "Text": item content
        "LanguageCode": supported language codes are ['en', 'es', 'fr', 'de', 'it', 'pt', 'ar', 'hi', 'ja', 'ko', 'zh', 'zh-TW']
    context: object, optional
        Lambda Context runtime methods and attributes
    Returns
    ------
    sentiment, valid values are "POSITIVE" | "NEGATIVE" | "NEUTRAL" | "MIXED"
    """
    logger.info('Calling get_sentiment with event')
    logger.info(event)

    # Use UTF-8 encoding for comprehend
    if 'Text' in event:
        text = str(event['Text'])
    else:
        logger.error("There is no Text!")
        raise Exception('Please provide Text!')

    # Check if LanguageCode is supported
    if 'LanguageCode' in event:
        LanguageCode = event['LanguageCode']
    else:
        logger.error("There is no Language Code!")
        raise Exception('Please provide a Language Code!')
    if not (LanguageCode in supportedLanguageCodes):
        logger.error("Language Code not supported!")
        raise Exception('Language Code not supported!')

    try:
        response = comprehend.detect_sentiment(Text=text, LanguageCode=LanguageCode)
    except ClientError as e:
        logger.error("Received error: %s", e, exc_info=True)
        raise
    except ParamValidationError as e:
        logger.error("The provided parameters are incorrect: %s", e, exc_info=True)
        raise

    return response['Sentiment']
