import logging
import json
import time
import boto3
import base64
from botocore.exceptions import ClientError
import os
import requests
import datetime as dt
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import csv
import codecs
from io import StringIO 
import tempfile
import pickle

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3') 
bucket_prefix = "factchecks-"
newfactchecks_folder = "new/"
factchecker_filename = "factchecker.csv"
factchecks_prefix = "factchecks_"
doc2vec_models_prefix = "model_sim_"
model_languages = ["de"] # defines for which languages should be supported with machine learnig models
stopword_languages = {"de": "german"}
hyper_parameter = [ {"vector_size": 40, "min_count": 2, "epochs": 100},
                    {"vector_size": 20, "min_count": 2, "epochs": 100},
                    {"vector_size": 80, "min_count": 2, "epochs": 100},
                    {"vector_size": 40, "min_count": 1, "epochs": 100},
                    {"vector_size": 40, "min_count": 3, "epochs": 100},
                    {"vector_size": 40, "min_count": 2, "epochs": 50},
                    {"vector_size": 40, "min_count": 2, "epochs": 20}]


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


# return bucket name for storing factchecks and models
def get_factcheckBucketName():
    bucket_name = bucket_prefix+os.environ['STAGE']
    try:
        s3_resource.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})
    return bucket_name

# store a csv in S3
def store_df(dict_list, csv_name):
    bucket = get_factcheckBucketName()
    csv_buffer = StringIO() 
    dict_writer = csv.DictWriter(csv_buffer, fieldnames=dict_list[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(dict_list)    
    s3_resource.Object(bucket, csv_name).put(Body=csv_buffer.getvalue())

# read a csv from S3 and return a dataframe
def read_df(csv_name):
    bucket = get_factcheckBucketName()
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=csv_name)
        dict_reader = csv.DictReader(codecs.getreader("utf-8")(obj["Body"]))
        # get a list of dictionaries from dct_reader
        csv_dict = list(dict_reader)
        return csv_dict
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.error('Error {} reading {} in bucket {}.'.format(e, csv_name, bucket))
        return []

# read model from S3
def read_model(model_name):
    bucket = get_factcheckBucketName()
    object = s3_resource.Object(bucket,model_name).get()
    serializedObject = object['Body'].read()

    #Deserialize the retrieved object
    model = pickle.loads(serializedObject)
    return model

# store model in S3
def save_model(model, model_name):
    bucket = get_factcheckBucketName()
    pickle_byte_obj = pickle.dumps(model) 
    s3_resource.Object(bucket, model_name).put(Body=pickle_byte_obj)

# convert a factcheck from json to df
def json2df(factcheck_json):
    factcheck_df = []

    # Check if the search was successful
    if 'claims' in factcheck_json:
        for article in factcheck_json['claims']:
            text=" "
            if 'text' in article:
                text=article['text']
                text = text.replace("\"", "")                
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
                        reviewDate = article['claimReview'][0]['reviewDate']
                    if 'textualRating' in article['claimReview'][0]:
                        textualRating=article['claimReview'][0]['textualRating']
                    if 'languageCode' in article['claimReview'][0]:
                        languageCode=article['claimReview'][0]['languageCode']

            df = {  'claim_text' : str(text),
                    'claimant' : claimant,
                    'claimDate' : claimDate,
                    'review_publisher' : name,
                    'review_site' : site,
                    'review_url' : url,
                    'review_title' : title,
                    'review_reviewDate' : reviewDate,
                    'review_textualRating' : textualRating,
                    'review_languageCode' : languageCode
                }
            factcheck_df.append(df)
        
    return factcheck_df


# Call Google API for updating Fact Checks
def get_googleapi_sync(language_code="de", maxAgeDays=0, reviewPublisherSiteFilter="", pageToken=""):
    pageSize = 10  # Count of returned results
    parameters = {"languageCode": language_code, "pageSize": pageSize, "pageToken": pageToken, "key": get_secret()}
    if maxAgeDays>0:
        parameters['maxAgeDays'] = maxAgeDays
    if reviewPublisherSiteFilter != "":
        parameters['reviewPublisherSiteFilter'] = reviewPublisherSiteFilter
    
    response = requests.get("https://factchecktools.googleapis.com/v1alpha1/claims:search", params=parameters)

    return response.json()


# lambda for updating lists of factchecks, factchecker and models
def update_factcheck_models(event, context):
    # read current list of factcheckers
    df_factchecker = read_df(factchecker_filename)
    # read new factchecks, extract the factchecker and include them in the factchecker-list
    bucket_resource = s3_resource.Bucket(get_factcheckBucketName())
    files = list(bucket_resource.objects.filter(Prefix=newfactchecks_folder))
    new_factchecker = False
    for f in files:
        obj = f.get()
        factcheck_json = json.load(obj['Body'])
        factcheck_df = json2df(factcheck_json)
        for row in factcheck_df:
            factchecker_exists = False
            for factchecker_row in df_factchecker:
                if row["review_site"] == factchecker_row['Factchecker']:
                    factchecker_exists = True
                    break
            if factchecker_exists == False:
                df_factchecker.append({'Factchecker': row["review_site"]})
                new_factchecker = True
        f.delete()
    # store factchecker if there are new ones
    if new_factchecker:
        store_df(df_factchecker, factchecker_filename)

    # update list of factchecks
    for LC in model_languages:
        df_factchecks = read_df(factchecks_prefix+LC+".csv")
        # determine the count of days until the last update
        if len(df_factchecks)==0:
            days=0 # 0 means all available fatchecks will be downloaded
        elif new_factchecker:
            days=0 # 0 means all available fatchecks will be downloaded
        else:
            # find the most recent date
            recent_date = dt.datetime.now(dt.timezone.utc)-relativedelta(years=5) # use at most the factchecks of the last 5 years
            for d in df_factchecks:
                try:
                    date = parse(d['review_reviewDate'])
                except:
                    continue
                if date>recent_date:
                    recent_date = date
            today = dt.datetime.now(dt.timezone.utc)
            days = int((today - recent_date).days)+1
        # get factchecks from all Fact Checker
        for row in df_factchecker:
            pageToken=""
            logger.info("Get reviews from "+row['Factchecker'])
            while True:
                response_json = get_googleapi_sync( language_code=LC, 
                                                    maxAgeDays=days, 
                                                    reviewPublisherSiteFilter=row['Factchecker'],
                                                    pageToken=pageToken)
                df_page = json2df(response_json)
                for fc in df_page:
                    if fc not in df_factchecks:
                        df_factchecks.append(fc)
                if 'nextPageToken' in response_json:
                    pageToken = response_json['nextPageToken']
                else:
                    pageToken=""
                if pageToken=="":
                    break
                time.sleep(1)
        if len(df_factchecks)>0:
            store_df(df_factchecks, factchecks_prefix+LC+".csv")
            # prepare data for training
            # stoplist = list(string.punctuation)
            # stoplist += stopwords.words(stopword_languages[LC]) # TODO Download german stopwords
            # documents_train = []
            # for i, row in df_factchecks.iterrows():
            #     tokens = gensim.utils.simple_preprocess(row["claim_text"])
                # Remove stop words
            #     words = [w for w in tokens if not w in stoplist]
                # For training data, add tags
            #     documents_train.append(gensim.models.doc2vec.TaggedDocument(words, [i]))
            # model = gensim.models.doc2vec.Doc2Vec(  vector_size=hyper_parameter[0]["vector_size"], 
            #                                         min_count=hyper_parameter[0]["min_count"], 
            #                                         epochs=hyper_parameter[0]["epochs"])
            # model.build_vocab(documents_train)
            # model.train(documents_train, total_examples=model.corpus_count, epochs=model.epochs)
            # save_model(model, doc2vec_models_prefix+LC)
