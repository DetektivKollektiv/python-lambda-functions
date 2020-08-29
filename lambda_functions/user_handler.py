from crud import operations

def delete_user(event, context, session=None):
    """Deletes a user from DB and Cognito.

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    try:
        operations.delete_user(event, session)

        response = {
            "statusCode": 200
        }

    except Exception as exception:
        response = {
            "statusCode": 500,
            "body": "User could not be deleted. Exception: {}".format(exception)
        }
    
    response_cors = operations.set_cors(response, event)
    return response_cors
