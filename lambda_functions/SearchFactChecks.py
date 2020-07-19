import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Search Fact Checks
def get_FactChecks(event, context):
    logger.info('Calling get_FactChecks with event')
    logger.info(event)

    # Check if key phrases are available
    if 'KeyPhrases' in event:
        keyPhrases = event['KeyPhrases']
    else:
        logger.error("There are no key phrases!")
        raise Exception('Please provide key phrases!')

    # Check if LanguageCode is available
    if 'LanguageCode' in event:
        LanguageCode = event['LanguageCode']
    else:
        logger.error("There is no Language Code!")
        raise Exception('Please provide a Language Code!')

    pageSize = 3  # Count of returned results
    query = ""
    for phrase in keyPhrases:
        query += "\"" + phrase + "\" "

    parameters = {"query": query, "languageCode": LanguageCode, "pageSize": pageSize, "key": os.environ.get('API_KEY')}
    response = requests.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params=parameters)

    # Get the response data as a python object. Verify that it's a dictionary.
    claims = response.json()['claims']

    return claims
