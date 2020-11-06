import aiohttp
import asyncio
import logging
import json
import time
import boto3
import base64
import re
from botocore.exceptions import ClientError
from uuid import uuid4
import os
import requests
import pandas as pd 
from io import StringIO 
from io import BytesIO
from nltk.corpus import stopwords
import string
import gensim
from gensim.similarities.index import AnnoyIndexer


logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3') 
bucket = "factchecks"
bucket_resource = s3_resource.Bucket(bucket)
newfactchecks_folder = "new/"
factchecker_filename = "factchecker.csv"
factchecks_prefix = "factchecks_.csv"
doc2vec_models_prefix = "model_sim_"
model_languages = ["de"] # defines for which languages should be supported with machine learnig models
stopword_languages = {"de": "german"}
hyper_parameter = [ {"vector_size": 50, "min_count": 2, "epochs": 100},
                    {"vector_size": 25, "min_count": 2, "epochs": 100},
                    {"vector_size": 100, "min_count": 2, "epochs": 100},
                    {"vector_size": 50, "min_count": 1, "epochs": 100},
                    {"vector_size": 50, "min_count": 3, "epochs": 100},
                    {"vector_size": 50, "min_count": 2, "epochs": 50},
                    {"vector_size": 50, "min_count": 2, "epochs": 20}]

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
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            return decoded_binary_secret


# Call Google API for Fact Check search
async def call_googleapi(session, search_terms, language_code):
    pageSize = 10  # Count of returned results
    query = ""
    for term in search_terms:
        query += "\"" + term + "\" "
    parameters = {"query": query, "languageCode": language_code,
                  "pageSize": pageSize, "key": get_secret()}
    response = await session.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params=parameters)

    return await response.json(), search_terms


# Get best fitting fact check article
async def get_article(search_terms, LanguageCode):
    article_bestfit = ""
    count_bestfit = 1  # minimum fit should be at least 2 search terms in the claim

    # combine Google API calls in one session
    # TODO consider to do that not for one lambda call, but for as much API calls as possible
    async with aiohttp.ClientSession() as session:
        # for or with would “break” the nature of await in the coroutine
        for f in asyncio.as_completed([call_googleapi(session, terms, LanguageCode) for terms in search_terms]):
            response_json, used_terms = await f

            # Check if the search was successful
            if 'claims' in response_json:
                # verify if the fact check articles fit to search terms
                # consider that there could be multiple equal entries in terms
                for article in response_json['claims']:
                    unique_terms = []
                    if 'text' in article:
                        for term in used_terms:
                            if term not in unique_terms:
                                if re.search(term, article['text']):
                                    unique_terms.append(term)
                        if len(unique_terms) > count_bestfit:
                            article_bestfit = article
                            count_bestfit = len(unique_terms)
                # Store received factchecks in a bucket to be used for training a model to assess similarity between claims and factchecks
                body = json.dumps(response_json)
                key = newfactchecks_folder+str(uuid4())
                try:
                    s3_response = s3_client.put_object(Body=body, Bucket=bucket, Key=key)
                    logger.info(s3_response)
                except Exception as e:
                    logger.error('Error {} putting object {} in bucket {}.'.format(e, key, bucket))

    return article_bestfit


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

    loop = asyncio.get_event_loop()
    factcheck = loop.run_until_complete(
        get_article(search_terms, LanguageCode))
    claims.append(factcheck)

    return claims

# store a csv in S3
def store_df(csv_df, csv_name):
    csv_buffer = StringIO() 
    csv_df.to_csv(csv_buffer) 
    s3_resource.Object(bucket, csv_name).put(Body=csv_buffer.getvalue())

# read a csv from S3 and return a dataframe
def read_df(csv_name):
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=csv_name)
        csv_df = pd.read_csv(obj['Body'])
        return csv_df
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.error('Error {} reading {} in bucket {}.'.format(e, csv_name, bucket))
        return pd.DataFrame()

# read model from S3
def read_model(model_name):
    obj = s3_client.get_object(Bucket=bucket, Key=model_name)
    model = gensim.models.doc2vec.Doc2Vec.load(BytesIO(obj['Body'].read()))
    return model

# store model in S3
def save_model(model, model_name):
    obj_model = BytesIO()
    model.save(obj_model)
    s3_client.put_object(Body=obj_model, Bucket=bucket, Key=model_name)

# convert a factcheck from json to df
def json2df(factcheck_json):
    factcheck_df = pd.DataFrame()

    # Check if the search was successful
    if 'claims' in factcheck_json:
        for article in factcheck_json['claims']:
            text=" "
            if 'text' in article:
                text=article['text']
            claimant=" "
            if 'claimant' in article:
                claimant=article['claimant']
            claimDate=" "
            if 'claimDate' in article:
                claimDate=article['claimDate']

            name=" "
            site=" "
            url=" "
            title=" " 
            reviewDate=""
            textualRating=" "
            languageCode=" "
            if 'claimReview' in article:
                if len(article['claimReview'])>0:
                    if 'publisher' in article['claimReview'][0]:
                        if 'name' in article['claimReview'][0]['publisher']:
                            name=article['claimReview'][0]['publisher']['name']
                        if 'site' in article['claimReview'][0]['publisher']:
                            site=article['claimReview'][0]['publisher']['site']
                    if 'url' in article['claimReview'][0]:
                        url=article['claimReview'][0]['url']
                    if 'title' in article['claimReview'][0]:
                        title=article['claimReview'][0]['title']
                    if 'reviewDate' in article['claimReview'][0]:
                        reviewDate=article['claimReview'][0]['reviewDate']
                    if 'textualRating' in article['claimReview'][0]:
                        textualRating=article['claimReview'][0]['textualRating']
                    if 'languageCode' in article['claimReview'][0]:
                        languageCode=article['claimReview'][0]['languageCode']

            df = pd.DataFrame({  'claim_text' : str(text),
                                 'claimant' : claimant,
                                 'claimDate' : claimDate,
                                 'review_publisher' : name,
                                 'review_site' : site,
                                 'review_url' : url,
                                 'review_title' : title,
                                 'review_reviewDate' : reviewDate,
                                 'review_textualRating' : textualRating,
                                 'review_languageCode' : languageCode},
                                index=[0])
            factcheck_df=factcheck_df.append(df, ignore_index=True)
        
    return factcheck_df


# Call Google API for updating Fact Checks
def get_googleapi_sync(language_code="de", maxAgeDays=0, reviewPublisherSiteFilter=""):
    pageSize = 10  # Count of returned results
    parameters = {"languageCode": language_code, "pageSize": pageSize, "key": get_secret()}
    if maxAgeDays>0:
        parameters['maxAgeDays'] = maxAgeDays
    if reviewPublisherSiteFilter != "":
        parameters['reviewPublisherSiteFilter'] = reviewPublisherSiteFilter
    
    response = requests.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params=parameters)

    return response.json()


# lambda for updating lists of factchecks, factchecker and models
def update_factcheck_models(event, context):
    maxAgeDays = event['pathParameters']['maxAgeDays']
    # read current list of factcheckers
    df_factchecker = read_df(factchecker_filename)
    # read new factchecks, extract the factchecker and include them in the factchecker-list
    files = list(bucket_resource.objects.filter(Prefix=newfactchecks_folder))
    new_factchecker = False
    for f in files:
        obj = f.get()
        factcheck_json = json.load(obj['Body'])
        factcheck_df = json2df(factcheck_json)
        for i, row in factcheck_df.iterrows():
            if row["review_site"] not in df_factchecker.values: 
                df = pd.DataFrame({'Factchecker': row["review_site"]}, index=[0])
                df_factchecker=df_factchecker.append(df, ignore_index=True)
                new_factchecker = True
        f.delete()
    # store factchecker if there are new ones
    if new_factchecker:
        store_df(df_factchecker, factchecker_filename)

    # update list of factchecks
    for LC in model_languages:
        df_factchecks = pd.DataFrame()
        # get factchecks from all Fact Checker
        for i, row in df_factchecker.iterrows():
            pageToken=""
            logger.info("Get reviews from "+row['Factchecker'])
            while True:
                response_json = get_googleapi_sync( language_code=LC, 
                                                    maxAgeDays=maxAgeDays, 
                                                    reviewPublisherSiteFilter=row['Factchecker'])
                df_page = json2df(response_json)
                df_factchecks = df_factchecks.append(df_page, ignore_index=True)
                if 'nextPageToken' in response_json:
                    pageToken = response_json['nextPageToken']
                if pageToken=="":
                    break
                time.sleep(1)
        store_df(df_factchecks, factchecks_prefix+LC)
        # prepare data for training
        stoplist = list(string.punctuation)
        stoplist += stopwords.words(stopword_languages[LC])
        documents_train = []
        for i, row in df_factchecks.iterrows():
            tokens = gensim.utils.simple_preprocess(row["claim_text"])
            # Remove stop words
            words = [w for w in tokens if not w in stoplist]
            # For training data, add tags
            documents_train.append(gensim.models.doc2vec.TaggedDocument(words, [i]))
        model = gensim.models.doc2vec.Doc2Vec(  vector_size=hyper_parameter[0]["vector_size"], 
                                                min_count=hyper_parameter[0]["min_count"], 
                                                epochs=hyper_parameter[0]["epochs"])
        model.build_vocab(documents_train)
        model.train(documents_train, total_examples=model.corpus_count, epochs=model.epochs)
        save_model(model, doc2vec_models_prefix+LC)
