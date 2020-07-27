import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Call Google API for Fact Check search
def call_googleapi(search_terms, language_code):
    pageSize = 3  # Count of returned results
    query = ""
    for term in search_terms:
        query += "\"" + term + "\" "
    parameters = {"query": query, "languageCode": language_code, "pageSize": pageSize, "key": os.environ.get('API_KEY')}
    return requests.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params=parameters)


# Search Fact Checks
def get_FactChecks(event, context):
    claims = []
    logger.info('Calling get_FactChecks with event')
    logger.info(event)

    # Check if key phrases are available
    if 'KeyPhrases' in event:
        search_terms = event['KeyPhrases']
    else:
        logger.error("There are no key phrases!")
        raise Exception('Please provide key phrases!')

    # Check if LanguageCode is available
    if 'item' in event:
        if 'language' in event['item']:
            LanguageCode = event['item']['language']
        else:
            logger.error("There is no language!")
            raise Exception('Please provide a language!')
    else:
        logger.error("There is no item!")
        raise Exception('Please provide an item!')

    response = call_googleapi(search_terms, LanguageCode)

    # Check if the search was successful
    # Get the response data as a python object. Verify that it's a dictionary.
    response_json = response.json()
    if 'claims' in response_json:
        claims = response_json['claims']
    # if the search was not successful, try again with entities as search terms
    elif 'Entities' in event:
        search_terms = event['Entities']
        response = call_googleapi(search_terms, LanguageCode)
        response_json = response.json()
        if 'claims' in response_json:
            claims = response_json['claims']
    else:
        logger.error("There are no search results!")

    return claims
