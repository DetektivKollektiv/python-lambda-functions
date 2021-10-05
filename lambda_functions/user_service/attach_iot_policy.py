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
            "Action": "iot:Subscribe",
            "Resource": ""
        }
    ]
}

POLICY_DOCUMENT_STRING_FORMAT = "arn:aws:iot:eu-central-1:891514678401:{0}"


def attach_iot_policy(event, context):
    try:
        helper.log_method_initiated("Attach IoT policy.", event, logger)

        try:
            cognito_identity = helper.get_cognito_identity_from_event(event)
        except Exception:
            return BadRequest(event, "Cognito identity ID was not found in event.").to_json_string()

        try:
            user_id = helper.cognito_id_from_event(event)
        except Exception:
            return BadRequest(event, "User ID was not found in event.").to_json_string()

        client = BotoClientProvider().get_client('iot')

        # Get the policy for the current user or create it
        try:
            policy = client.get_policy(policyName=user_id)
        except client.exceptions.ResourceNotFoundException as e:
            resource = POLICY_DOCUMENT_STRING_FORMAT.format(user_id)

            policy_document["Statement"][0]["Resource"] = resource

            policy = client.create_policy(
                policyName=user_id, policyDocument=json.dumps(policy_document))

        attached_policies = client.list_attached_policies(
            target=cognito_identity)

        # If the policy is already attached to the current identity return
        if(policy['policyName'] in [attached_policy['policyName'] for attached_policy in attached_policies['policies']]):
            return Success(event).to_json_string()

        client.attach_policy(
            policyName=policy['policyName'], target=cognito_identity)

        return Success(event).to_json_string()

    except Exception as e:
        return InternalError(event, "Error attaching IoT policy.", e).to_json_string()
