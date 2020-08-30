from datetime import datetime
import os
import json


def get_date_time_now(is_test):
    if is_test:
        return datetime.now()
    else:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def set_cors(response, event, is_test):
    """Adds a CORS header to a response according to the headers found in the event.

    Parameters
    ----------
    response: dict
        The response to be modified
    event: dict
        The Lambda event

    Returns
    ------
    response: dict
        The modified response
    """
    if is_test:
        return event

    source_origin = None
    allowed_origins = os.environ['CORS_ALLOW_ORIGIN'].split(',')

    if 'headers' in event:
        if 'Origin' in event['headers']:
            source_origin = event['headers']['Origin']
        if 'origin' in event['headers']:
            source_origin = event['headers']['origin']

        if source_origin and source_origin in allowed_origins:
            if 'headers' not in response:
                response['headers'] = {}

            response['headers']['Access-Control-Allow-Origin'] = source_origin

    return response


def body_to_object(body, object):
    """Uses the request body to set the attributes of the specified object.

    Parameters
    ----------
    body: str, dict
        The request body (str or dict)
    object: Item, User, Review, Submission, etc.
        The object, e.g. an instance of the class Item or User

    Returns
    ------
    obj: Object
        The object with the set attributes
    """

    # Deserialize if body is string (--> Lambda called by API Gateway)
    if isinstance(body, str):
        body_dict = json.loads(body)
    else:
        body_dict = body

    # Load request body as dict and transform to Item object
    for key in body_dict:
        if type(body_dict[key]) != list:
            setattr(object, key, body_dict[key])

    return object


def cognito_id_from_event(event):
    """Extracts the cognito user id (=sub) from the event.

    Parameters
    ----------
    event: dict
        The Lambda event

    Returns
    ------
    user_id: str
        The user id
    """
    user_id = str(event['requestContext']['identity']
                  ['cognitoAuthenticationProvider']).split("CognitoSignIn:", 1)[1]
    return user_id


def log_method_initiated(method_name, event, logger):
    logger.info("Method {} initiated".format(method_name))
    logger.info("Event: {}".format(event))
