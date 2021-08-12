# External imports
import logging
import json

# Helper imports
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import tag_handler
from ml_service import SearchFactChecks, UpdateFactChecks

import boto3
import os

s3_client = boto3.client('s3')


def get_tags_for_item(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get tags by item id", event, logger)
    
    with Session() as session:

        try:
            # get id (str) from path
            id = event['pathParameters']['item_id']

            try:
                tag_objects = tag_handler.get_tags_by_itemid(id, session)

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

    response_cors = helper.set_cors(response, event)
    return response_cors


def post_tags_for_item(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Post tags by item id", event, logger)

    
    with Session() as session:

        # get list of existing tags
        tags_existing = []
        try:
            # get id (str) from path
            id = event['pathParameters']['item_id']

            tag_objects = tag_handler.get_tags_by_itemid(id, session)

            for obj in tag_objects:
                tags_existing.append(obj.to_dict()['tag'])
        except Exception as e:
            response = {
                "statusCode": 400,
                "body": "Could not get item ID. Check HTTP POST payload. Exception: {}".format(e)
            }

        # get list of posted tags
        body = event['body']

        if isinstance(body, str):
            body_dict = json.loads(body)
        else:
            body_dict = body
        if 'tags' in body_dict:
            tags_posted = body_dict['tags']
        else:
            tags_posted = []        

        # save tags
        if tags_posted != []:
            for str_tag in tags_posted:
                tag_handler.store_tag_for_item(id, str_tag, session)

        # create response
        tags_new = list(set(tags_posted)-set(tags_existing))
        tags_counter_increased = list(set(tags_posted)-set(tags_new))
        response = {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps({"added new tags": tags_new,"increased tag counter": tags_counter_increased})
        }

    response_cors = helper.set_cors(response, event)
    return response_cors


def download_taxonomy(LanguageCode):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stage = os.environ['STAGE']    

    if LanguageCode not in UpdateFactChecks.model_languages:
        logger.error("Language Code {} not supported!".format(LanguageCode))
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


def upload_tagreport(tagreport_json, LanguageCode):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stage = os.environ['STAGE']    

    if LanguageCode not in UpdateFactChecks.model_languages:
        logger.error("Language Code {} not supported!".format(LanguageCode))
        return {}

    # Write the tag-terms json file
    path = '/tmp/'
    os.chdir(path)
    tagreport_file_name = "tag_report_{}.json".format(LanguageCode)
    bucket = "factchecks-"+stage
    key = "tagging/"+tagreport_file_name
    with open(tagreport_file_name, "w") as f:
        json.dump(tagreport_json, f, ensure_ascii=False, indent=4)        
    # upload tag-terms json file
    s3_client.upload_file(tagreport_file_name, bucket, key)


def predict_tags(event, context):
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
        if LanguageCode not in UpdateFactChecks.model_languages:
            logger.error("Language Code {} not supported!".format(LanguageCode))
            return []
    else:
        logger.error("There is no Language Code!")
        return []
    taxonomy_json = download_taxonomy(LanguageCode)
    similarity_threshold = taxonomy_json["similarity-threshold"]

    for stopword in ["\"", ",", ".", "!", "?", "«", "»", "(", ")", "-"]:
        text = text.replace(stopword, " ")
    new_text = ""
    text_split = []
    for substr in text.split():
        if str.lower(substr) not in taxonomy_json["excluded-terms"]:
            new_text += substr+" "
            substr = str.lower(substr)
            text_split.append(substr)

    sim_input = []
    term2tags = []
    tags = []
    for category in taxonomy_json:
        if category == "similarity-threshold":
            continue
        if category == "excluded-terms":
            continue
        for tag in taxonomy_json[category]:
            for term in taxonomy_json[category][tag]:
                sim_input.append("\""+term+"\"" + ",\""+new_text+"\"")
                term2tags.append(tag)
                if (term.lower() in text_split) and (tag not in tags):
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
            if sim > similarity_threshold:
                if term2tags[ind] not in tags:
                    tags.append(term2tags[ind])
            ind = ind+1
    except Exception as e:
        logger.error('DocSim error: {}.'.format(e))
    return tags


# report which tags are in the database but not considered in the taxonomy
def create_tagreport(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Report tags not considered in taxonomy", event, logger)

    
    # list with tags in the database but not covered by the taxonomy
    terms_new = []
    with Session() as session:
        # read all tags from database
        tag_list = tag_handler.get_all_tags(session)

    for LanguageCode in UpdateFactChecks.model_languages:
        logger.info("LanguageCode: {}".format(LanguageCode))
        # Read language specific taxonomy
        taxonomy_json = download_taxonomy(LanguageCode)
        term_list = []
        term_test = ""
        # create list of terms already considered in taxonomy
        for category in taxonomy_json:
            if category == "similarity-threshold":
                continue
            for tag in taxonomy_json[category]:
                if tag.lower() not in term_list:
                    term_list.append(tag.lower())
                if category == "excluded-terms":
                    continue
                for term in taxonomy_json[category][tag]:
                    term = term.lower()
                    if term_test == "":
                        term_test = term
                    if term not in term_list:
                        term_list.append(term)
        tagreport_json = {"additional_tags": []}
        # Create list with tags not considered in taxonomy
        sim_input = []
        for tag in tag_list:
            tag = str.lower(tag.tag)
            if (tag not in term_list) and (tag not in terms_new):
                # test if the tag is in the model vocabulary
                sim_input.append("\""+term_test+"\"" + ",\""+tag+"\"")
                terms_new.append(tag)
        # call sagemaker endpoint for similarity prediction to verify if tags are in vocabulary
        while (len(sim_input))>0:
            # do similarity prediction for 100 tags at most
            payload_list = sim_input[0:100]
            payload = '\n'.join(payload_list)
            try:
                response = SearchFactChecks.post_DocSim(LanguageCode, payload)
                if not response.ok:
                    raise Exception('Received status code {}.'.format(response.status_code))
                result = response.text
                scores = json.loads(result)
                for score in scores:
                    tag = terms_new.pop(0)
                    sim_input.pop(0)
                    # Is tag in vocabulary?
                    if score != '0.00':
                        tagreport_json["additional_tags"].append(tag)
                        logger.info("Taxonomy does not consider tag {}".format(tag))
            except Exception as e:
                logger.error('DocSim error: {}.'.format(e))
                continue
        upload_tagreport(tagreport_json, LanguageCode)
