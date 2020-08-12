import logging
import json
import requests
import boto3
import base64
import re
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/
def get_secret():
    secret_name = "/factcheck/search/Google_API__KEY"
    region_name = "eu-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)['FactCheckSearch_API_KEY']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret


# Call Google API for Fact Check search
def call_googleapi(search_terms, language_code):
    pageSize = 1  # Count of returned results
    query = ""
    for term in search_terms:
        query += "\"" + term + "\" "
    parameters = {"query": query, "languageCode": language_code, "pageSize": pageSize, "key": get_secret()}
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
            # verify if the fact check articles fit to search terms
            # consider that there could be multiple equal entries in terms
            unique_terms = []
            for article in response_json['claims']:
                if 'text' in article:
                    for term in terms:
                        if term not in unique_terms:
                            if re.search(term, article['text']):
                                unique_terms.append(term)
            if len(unique_terms) > 1:
                claims.append(article)

    return claims
