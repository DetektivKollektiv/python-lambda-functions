import os
import requests
from core_layer.helper import get_google_api_key

API_URL_GOOGLE = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
THREAT_PREFIX_GOOGLE = "GOOGLE:"

def threatcheck(url):
    """ Checks the URL for various threats
     Parameters
    ----------
     url:
        string
    Returns
    ------
        threat or None
    """
    result = get_googleapi_safebrowsing_threat(url)
    return result

def get_googleapi_safebrowsing_threat(url):
    """ Calls Google API for checking unsafe urls
    Parameters
    ----------
    url:
        string, required
    Returns
    ------
        for threat urls:
            'GOOGLE:' followed by threat type (e.g. GOOGLE:MALWARE).
        in case of failing API call:
            GOOGLE:N/A
        for no threat urls:
            None
    """
    body = {
        "client": {
            "clientId": "codetect",
            "clientVersion": "1.5.2"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "THREAT_TYPE_UNSPECIFIED",
                            "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    ## first check if google api key is stored in environment parameter
    key = None
    if "UNITTEST_GOOGLE_API_KEY" in os.environ:
        key = os.environ["UNITTEST_GOOGLE_API_KEY"]
    else:
        key = get_google_api_key()

    response = requests.post(API_URL_GOOGLE + "?key=" + key, None, body)

    if response.status_code == 200:
        result_json = response.json()
        if 'matches' in result_json:
            threat = THREAT_PREFIX_GOOGLE + result_json['matches'][0]['threatType']
        else:
            threat = None
    else:
        threat = THREAT_PREFIX_GOOGLE + "N/A"

    return threat
