import boto3
import logging
import requests
import os
import json
from botocore.exceptions import ClientError, ParamValidationError
from operator import itemgetter

supportedLanguageCodes = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ar', 'hi', 'ja', 'ko', 'zh', 'zh-TW']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client(service_name='comprehend', region_name='eu-central-1')


def post_TopicalPageRank(language, data):
    stage = os.environ['STAGE']    
    if stage == 'prod':
        link = 'https://api.detektivkollektiv.org/ml_model_service/models/'
    else:
        link = 'https://api.{}.detektivkollektiv.org/ml_model_service/models/'.format(stage)
    if language == "de":
        url = link+"TopicalPageRank"
    else:
        logger.error("Language not supported by TopicalPageRank!")
        return {}

    headers = {"content-type": "text/csv", "Accept": "text/csv"}
    prediction = requests.post(url, headers=headers, data=data.encode('utf-8'))
    if not prediction.ok:
        raise Exception('Received status code {}.'.format(prediction.status_code))
    result = prediction.text
    result = json.loads(result)
    # convert to a structure according comprehend
    keyphrases = []
    for item in result:
        phrase = {}
        phrase["Text"] = item[0]
        phrase["Score"] = item[1]
        keyphrases.append(phrase)
    response = {}
    response["KeyPhrases"] = keyphrases
    return response

def get_phrases(event, context):
    """Detect Key Phrases
    entities can be of type PERSON | LOCATION | ORGANIZATION | COMMERCIAL_ITEM | EVENT | DATE | QUANTITY | TITLE | OTHER
    Parameters
    ----------
    event: dict, required
        "Text": item content
        "LanguageCode": supported language codes are ['en', 'es', 'fr', 'de', 'it', 'pt', 'ar', 'hi', 'ja', 'ko', 'zh', 'zh-TW']
    context: object, optional
        Lambda Context runtime methods and attributes
    Returns
    ------
    list of strings with key phrases
    """
    logger.info('Calling get_phrases with event')
    logger.info(event)

    # Use UTF-8 encoding for comprehend
    if 'Text' in event:
        text = str(event['Text'])
    else:
        logger.error("There is no Text!")
        return []

    # Check if LanguageCode is supported
    if 'LanguageCode' in event:
        LanguageCode = event['LanguageCode']
    else:
        logger.error("There is no Language Code!")
        return []
    if not (LanguageCode in supportedLanguageCodes):
        logger.error("Language Code not supported!")
        return []

    response = {}
    try:
        response = post_TopicalPageRank(LanguageCode, text)
    except Exception as e:
        logger.error("TopicalPageRank error: %s", e, exc_info=True)
    if not "KeyPhrases" in response:
        try:
            response = comprehend.detect_key_phrases(Text=text, LanguageCode=LanguageCode)
        except ClientError as e:
            logger.error("Received error: %s", e, exc_info=True)
            return []
        except ParamValidationError as e:
            logger.error("The provided parameters are incorrect: %s", e, exc_info=True)
            return []

    # sort list of key phrases according the score
    keyPhrases_sorted = sorted(response["KeyPhrases"], key=itemgetter('Score'), reverse=True)

    # respond at most 5 key phrases
    keyPhrases_sorted = keyPhrases_sorted[:min(3, len(keyPhrases_sorted))]

    # extract the strings
    keyPhrases_strings = []
    for obj in keyPhrases_sorted:
        keyPhrases_strings.append(obj.get('Text'))

    return keyPhrases_strings
