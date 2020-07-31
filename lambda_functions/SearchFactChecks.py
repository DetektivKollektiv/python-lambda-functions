import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Call Google API for Fact Check search
def call_googleapi(search_terms, language_code):
    pageSize = 1  # Count of returned results
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

    search_terms = []
    # Check if search terms are available
    if 'TitleEntities' in event:
        search_terms.append(event['TitleEntities'])
    if 'KeyPhrases' in event:
        search_terms.append(event['KeyPhrases'])
    if 'Entities' in event:
        search_terms.append(event['Entities'])

    for terms in search_terms:
        response = call_googleapi(terms, LanguageCode)
        # Check if the search was successful
        # Get the response data as a python object. Verify that it's a dictionary.
        response_json = response.json()
        if 'claims' in response_json:
            claims.append(response_json['claims'][0])

    return claims
