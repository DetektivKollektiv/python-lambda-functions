import logging
import json
from core_layer import helper
from core_layer.responses import BadRequest, InternalError, Success
from core_layer.boto_client_provider import BotoClientProvider


logger = logging.getLogger()
logger.setLevel(logging.INFO)

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "iot:*",
            "Resource": ""
        }
    ]
}

POLICY_DOCUMENT_STRING_FORMAT = "arn:aws:iot:eu-central-1:891514678401:{0}"


ERROR_MSG_IDENTIY_ID_MISSING = "Cognito identity ID was not found in event."
ERROR_MSG_USER_ID_MISSING = "User ID was not found in event."
ERROR_MSG_EXCEPTION = "Error attaching IoT policy."
INFO_MSG_POLICY_ALREADY_ATTACHED = "IoT policy is already attached to the current identity."
INFO_MSG_POLICY_ATTACHED = "Successfully attached IoT policy to identity."


def attach_iot_policy(event, context):
    try:
        helper.log_method_initiated("Attach IoT policy.", event, logger)

        try:
            cognito_identity = helper.get_cognito_identity_from_event(event)
        except Exception:
            logger.error(ERROR_MSG_IDENTIY_ID_MISSING)
            return BadRequest(event, ERROR_MSG_IDENTIY_ID_MISSING).to_json_string()

        try:
            user_id = helper.cognito_id_from_event(event)
        except Exception:
            logger.error(ERROR_MSG_USER_ID_MISSING)
            return BadRequest(event, ERROR_MSG_USER_ID_MISSING).to_json_string()

        client = BotoClientProvider().get_client('iot')

        # Get the policy for the current user or create it
        try:
            policy = client.get_policy(policyName=user_id)
        except client.exceptions.ResourceNotFoundException as e:
            resource = POLICY_DOCUMENT_STRING_FORMAT.format(user_id)

            policy_document['Statement'][0]['Resource'] = resource

            policy = client.create_policy(
                policyName=user_id, policyDocument=json.dumps(policy_document))

        attached_policies = client.list_attached_policies(
            target=cognito_identity)

        # If the policy is already attached to the current identity return
        if(policy['policyName'] in [attached_policy['policyName'] for attached_policy in attached_policies['policies']]):
            logger.info(INFO_MSG_POLICY_ALREADY_ATTACHED)
            return Success(event).to_json_string()

        client.attach_policy(
            policyName=policy['policyName'], target=cognito_identity)

        logger.info(INFO_MSG_POLICY_ATTACHED)
        return Success(event).to_json_string()

    except Exception as e:
        logger.exception(ERROR_MSG_EXCEPTION)
        return InternalError(event, ERROR_MSG_EXCEPTION, e).to_json_string()
