import logging
import json
import boto3
import re
from botocore.exceptions import ClientError
from uuid import uuid4
import os
import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from core_layer.helper import get_google_api_key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sm_client = boto3.client('sagemaker-runtime', region_name='eu-central-1')
endpoint_prefix = "fc-sim-"
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
bucket_prefix = "factchecks-"
newfactchecks_folder = "new/"


# return bucket name for storing factchecks and models

def get_factcheckBucketName():
    bucket_name = bucket_prefix+os.environ['STAGE']
    try:
        s3_resource.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
                                'LocationConstraint': 'eu-central-1'})
    return bucket_name

# Call Google API for Fact Check search


async def call_googleapi(session, search_terms, language_code):
    pageSize = 10  # Count of returned results
    query = ""
    for term in search_terms:
        # query += "\"" + term + "\" "
        query += term + " "
    parameters = {"query": query, "languageCode": language_code,
                  "pageSize": pageSize, "key": get_google_api_key()}
    response = await session.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params=parameters)

    return await response.json(), search_terms


def post_DocSim(language, data):
    stage = os.environ['STAGE']
    if stage == 'prod':
        host = 'api.codetekt.org'
    else:
        host = 'api.{}.codetekt.org'.format(stage)
    if language == "de":
        url = "https://"+host+"/ml_model_service/models/DocSim"
    else:
        logger.error("Language not supported!")
        raise Exception('Language not supported by DocSim!')
    headers = {"content-type": "text/csv", "Accept": "text/csv"}
    auth = BotoAWSRequestsAuth(
        aws_host=host,
        aws_region="eu-central-1",
        aws_service="execute-api"
    )

    response = requests.post(url, headers=headers,
                             data=data.encode('utf-8'), auth=auth)

    return response

# Get best fitting fact check article


async def get_article(search_terms, LanguageCode):
    import aiohttp
    import aiodns
    import asyncio

    article_bestfit = ""
    count_bestfit = 1  # minimum fit should be at least 2 search terms in the claim
    bucket = get_factcheckBucketName()
    article_bestsim = ""
    bestsim = 0.0

    # combine Google API calls in one session
    # TODO consider to do that not for one lambda call, but for as much API calls as possible
    async with aiohttp.ClientSession() as session:
        # for or with would “break” the nature of await in the coroutine
        for f in asyncio.as_completed([call_googleapi(session, terms, LanguageCode) for terms in search_terms]):
            response_json, used_terms = await f

            # Check if the search was successful
            if 'claims' in response_json:
                sm_input = []
                # build input from search_terms for sagemaker
                sm_input_search = "\""
                for term in used_terms:
                    sm_input_search += term + " "
                sm_input_search += "\""
                # verify if the fact check articles fit to search terms
                # consider that there could be multiple equal entries in terms
                for article in response_json['claims']:
                    unique_terms = []
                    if 'text' in article:
                        for term in used_terms:
                            if term not in unique_terms:
                                try:
                                    if re.search(term, article['text']):
                                        unique_terms.append(term)
                                except:
                                    pass
                        if len(unique_terms) > count_bestfit:
                            article_bestfit = article
                            count_bestfit = len(unique_terms)

                        article_text = article['text'].replace("\"", "")
                        # input for article
                        if len(used_terms) > 1:
                            sm_input.append(sm_input_search +
                                            ",\""+article_text+"\"")
                # call sagemaker endpoint for similarity prediction
                try:
                    if sm_input == []:
                        raise Exception('Nothing to compare.')
                    payload = '\n'.join(sm_input)
                    response = post_DocSim(LanguageCode, payload)
                    if not response.ok:
                        raise Exception(
                            'Received status code {}.'.format(response.status_code))
                    result = response.text
                    scores = json.loads(result)
                    ind = 0
                    for score in scores:
                        if score == '':
                            continue
                        sim = float(score)
                        if sim > bestsim:
                            article_bestsim = response_json['claims'][ind]
                            bestsim = sim
                        ind = ind+1
                except Exception as e:
                    logger.error('DocSim error: {}.'.format(e))
                # Store received factchecks in a bucket to be used for training a model to assess similarity between claims and factchecks
                body = json.dumps(response_json)
                key = newfactchecks_folder+str(uuid4())
                try:
                    s3_response = s3_client.put_object(
                        Body=body, Bucket=bucket, Key=key)
                    logger.info(s3_response)
                except Exception as e:
                    logger.error(
                        'Error {} putting object {} in bucket {}.'.format(e, key, bucket))

    if bestsim > 0.7:
        return article_bestsim
    elif bestsim == 0.0:
        return article_bestfit
    else:
        return ""


# Search Fact Checks
def get_FactChecks(event, context):
    import asyncio

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
    if 'KeyPhrases' in event:
        search_terms.append(event['KeyPhrases'])
    if 'Entities' in event:
        search_terms.append(event['Entities'])

    loop = asyncio.get_event_loop()
    factcheck = loop.run_until_complete(
        get_article(search_terms, LanguageCode))

    # check if there is a title of the factcheck, if not, then take the textualRating
    if 'claimReview' in factcheck:
        if 'title' not in factcheck['claimReview'][0]:
            if 'textualRating' in factcheck['claimReview'][0]:
                factcheck['claimReview'][0]['title'] = factcheck['claimReview'][0]['textualRating']

    claims.append(factcheck)

    return claims
