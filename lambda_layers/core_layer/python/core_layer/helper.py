from datetime import datetime, timedelta
import os
import json
import base64
import boto3
from botocore.config import Config  # remove later
from botocore.exceptions import ClientError
from sqlalchemy import func

is_test = 'DEPLOYMENTMODE' not in os.environ


def get_date_time_now():
    return func.now()
    # TODO: Remove this method. Use func.now() and set create_time in model
    # https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    # TODO: Update to newer version of Sqlalchemy Aurora Library and adapt datemanagement accordingly


def get_date_time_one_hour_ago():
    dt = datetime.now() + timedelta(hours=-1)
    if is_test:
        return dt
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_date_time(dt):
    if is_test:
        return dt
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_date_time_str(dt):
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return dt


def set_cors(response, event):
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
        return response

    source_origin = None
    allowed_origins = os.environ['CORS_ALLOW_ORIGIN'].split(',')

    if 'headers' in event and event['headers'] is not None:
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


def get_secret(secret_name, region_name="eu-central-1"):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    config = Config(read_timeout=2, connect_timeout=2)  # remove later
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,  # remove comma later
        config=config  # remove later
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
            return get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            return decoded_binary_secret

# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/
def get_google_api_key():
    secret_name = "google/api_key"
    region_name = "eu-central-1"

    secret = get_secret(secret_name, region_name)
    return json.loads(secret)['Google_API_KEY']


def get_text_response(status_code: int, text: str, event):
    response = {
        "statusCode": status_code,
        'headers': {"content-type": "application/json; charset=utf-8"},
        "body": text
    }
    response = set_cors(response, event)
    return response
