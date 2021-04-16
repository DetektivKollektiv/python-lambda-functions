# External imports
import logging
import json
from uuid import uuid4
# Helper imports
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import item_handler, tag_handler
import SearchFactChecks

import boto3
import os
import tarfile
import csv
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')


def get_tags_for_item(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get tags by item id", event, logger)

    if session is None:
        session = get_db_session(is_test, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        try:
            tag_objects = tag_handler.get_tags_by_itemid(id, is_test, session)

            tags = []
            for obj in tag_objects:
                tags.append(obj.to_dict()['tag'])
        except Exception as e:
            response = {
                "statusCode": 404,
                "body": "No tags found. Exception: {}".format(e)
            }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get item ID. Check HTTP GET payload. Exception: {}".format(e)
        }
    body_json = {"Tags": tags}
    response = {
        "statusCode": 200,
        'headers': {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps(body_json)
    }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors

def post_tags_for_item(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Post tags by item id", event, logger)

    if session is None:
        session = get_db_session(is_test, None)

    tags_existing = []
    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        tag_objects = tag_handler.get_tags_by_itemid(id, is_test, session)

        for obj in tag_objects:
            tags_existing.append(obj.to_dict()['tag'])
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get item ID. Check HTTP POST payload. Exception: {}".format(e)
        }

    body = event['body']

    if isinstance(body, str):
        body_dict = json.loads(body)
    else:
        body_dict = body
    if 'tags' in body_dict:
        tags_posted = body_dict['tags']
    else:
        tags_posted = []        

    tags_new = list(set(tags_posted)-set(tags_existing))
    if tags_new != []:
        for str_tag in tags_new:
            tag_handler.store_tag_for_item(id, str_tag, is_test, session)

    tags_removed = list(set(tags_existing)-set(tags_posted))
    for str_tag in tags_removed:
        # search for tag in database
        tag = tag_handler.get_tag_by_content(str_tag, is_test, session)
        if tag is not None:
            tag_handler.delete_itemtag_by_tag_and_item_id(tag.id, id, is_test, session)

    response = {
        "statusCode": 200,
        'headers': {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps({"added tags": tags_new,"removed tags": tags_removed})
    }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors

def topics_to_json(event, context, is_test=False, session=None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Convert topics modelling output to json", event, logger)

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        logger.info('bucket: {}'.format(bucket))
        logger.info('key: {}'.format(key))
        # download new topic and term list
        download_path = '/tmp/'
        os.chdir(download_path)
        output_file_name = "output.tar.gz"
        s3_client.download_file(bucket, key, download_path+output_file_name)
        # extract topics and terms
        with tarfile.open(download_path+output_file_name) as tar:
            tar.extractall(download_path)
        new_topics_json = {}
        csv_file = csv.DictReader(open("topic-terms.csv"))
        for row in csv_file:
            category = "c"+row["topic"]
            tag = "t"+row["topic"]
            term = row["term"]
            if category not in new_topics_json:
                new_topics_json[category] = {}
            if tag not in new_topics_json[category]:
                new_topics_json[category][tag] = {}
            if term not in new_topics_json[category][tag]:
                new_topics_json[category][tag][term] = row["weight"]
        # Write the tag-terms json file
        new_json_file_name = "tag-terms_new.json"
        with open(new_json_file_name, "w") as f:
            json.dump(new_topics_json, f, indent=4)        
        # upload tag-terms json file
        destkey = 'topics/'+new_json_file_name
        s3_client.upload_file(new_json_file_name, bucket, destkey)

        # upload tag-terms json file
        destkey = 'topics/'+diff_json_file_name
        s3_client.upload_file(diff_json_file_name, bucket, destkey)

def download_taxonomy(LanguageCode):
    stage = os.environ['STAGE']    

    if not (LanguageCode in ["de"]):
        logger.error("Language Code not supported!")
        return {}

    # download taxonomy
    download_path = '/tmp/'
    os.chdir(download_path)
    taxonomy_file_name = "category-tag-terms-{}.json".format(LanguageCode)
    bucket = "factchecks-"+stage
    key = "tagging/"+taxonomy_file_name
    s3_client.download_file(bucket, key, download_path+taxonomy_file_name)
    with open(taxonomy_file_name, "r") as f:
        taxonomy_json = json.load(f)

    return taxonomy_json

def predict_tags(event, context, is_test=False, session=None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Predict tags for claim", event, logger)


    text = ""
    if 'Text' in event:
        text = str(event['Text'])
    if len(text) == 0:
        logger.error("There is no Text!")
        return []

    # Check if LanguageCode is supported
    if 'LanguageCode' in event:
        LanguageCode = event['LanguageCode']
    else:
        logger.error("There is no Language Code!")
        return []
    taxonomy_json = download_taxonomy(LanguageCode)

    for stopword in ["\"", ",", ".", "!", "?", "«", "»", "(", ")", "-"]:
        text = text.replace(stopword, " ")
    new_text = ""
    text_split = []
    for substr in text.split():
        if str.lower(substr) not in taxonomy_json["excluded-terms"]:
            new_text += substr+" "
            if substr != "5G":
                substr = str.lower(substr)
            text_split.append(substr)

    sim_input = []
    term2tags = []
    tags = []
    for category in taxonomy_json:
        if category == "unsorted-terms":
            continue
        if category == "excluded-terms":
            continue
        for tag in taxonomy_json[category]:
            for term in taxonomy_json[category][tag]:
                sim_input.append("\""+term+"\"" + ",\""+new_text+"\"")
                term2tags.append(tag)
                if (term in text_split) and (tag not in tags):
                    tags.append(tag)
    if tags != []:
        return tags
    # call sagemaker endpoint for similarity prediction
    try:
        if sim_input == []:
            raise Exception('Nothing to compare.')
        payload = '\n'.join(sim_input)
        response = SearchFactChecks.post_DocSim(LanguageCode, payload)
        if not response.ok:
            raise Exception('Received status code {}.'.format(response.status_code))
        result = response.text
        scores = json.loads(result)
        ind = 0
        for score in scores:
            if score == '':
                ind = ind+1
                continue
            sim = float(score)
            if sim > 0.7:
                if term2tags[ind] not in tags:
                    tags.append(term2tags[ind])
            ind = ind+1
    except Exception as e:
        logger.error('DocSim error: {}.'.format(e))
    return tags
