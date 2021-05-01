import os
import requests
import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import url_handler
from ml_service.SearchFactChecks import get_secret

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def threatcheck(url):
    result = get_googleapi_safebrowsing_threat(url)
    return result


# Call Google API for checking ussafe urls
def get_googleapi_safebrowsing_threat(url):
    body = {
        "client": {
            "clientId": "codetect",
            "clientVersion": "1.5.2"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "THREAT_TYPE_UNSPECIFIED", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    if 'DBNAME' not in os.environ:
        # todo fill key before execute the test
        key = ""
    else:
        key = get_secret();


    response = requests.post("https://safebrowsing.googleapis.com/v4/threatMatches:find?key=" + key, None, body)

    if response.status_code == 200:
        resultJson = response.json()
        if 'matches' in resultJson:
            threat = "GOOGLE:" + resultJson['matches'][0]['threatType']
        else:
            threat = None
    else:
        # todo@cba what to do?
        threat = "GOOGLE:N/A"

    return threat
