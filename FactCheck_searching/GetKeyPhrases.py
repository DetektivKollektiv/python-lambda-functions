import boto3
import logging
from botocore.exceptions import ClientError, ParamValidationError
from operator import itemgetter

supportedLanguageCodes = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ar', 'hi', 'ja', 'ko', 'zh', 'zh-TW']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client(service_name='comprehend', region_name='eu-central-1')


# Detect Key Phrases
# return a list of strings with the five key phrases with the highest score
def get_phrases(event, context):
    logger.info('Calling get_phrases with event')
    logger.info(event)

    # Use UTF-8 encoding for comprehend
    if 'Text' in event:
        text = str(event['Text'].encode(errors="ignore"))
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
        response = comprehend.detect_key_phrases(Text=text, LanguageCode=LanguageCode)
    except ClientError as e:
        logger.error("Received error: %s", e, exc_info=True)
        raise
    except ParamValidationError as e:
        logger.error("The provided parameters are incorrect: %s", e, exc_info=True)
        raise

    # sort list of key phrases according the score
    keyPhrases_sorted = sorted(response["KeyPhrases"], key=itemgetter('Score'), reverse=True)

    # respond at most 5 key phrases
    keyPhrases_sorted = keyPhrases_sorted[:min(5, len(keyPhrases_sorted))]

    # extract the strings
    keyPhrases_strings = []
    for obj in keyPhrases_sorted:
        keyPhrases_strings.append(obj.get('Text'))

    return keyPhrases_strings
