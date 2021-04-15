from twilio.twiml.messaging_response import MessagingResponse
from urllib import parse
import requests


def whatsapp_forwarding(event, context):
    """Whatsapp bot sending item to API

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
    API Gateway Lambda Proxy Output Format: application/xml

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    text = event['body']
    content = dict(parse.parse_qs(text))
    item = content['Body'][0].encode('utf-8')

    # Send to API
    url = "https://api.codetekt.org/stage/items"
    dk_api_response = requests.post(url, data=item)

    # Add a message
    resp = MessagingResponse()
    resp.message(
        "Thanks for submitting your item. Our detectives are checking it immediately")

    print(str(resp))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/xml",
        },
        "body": str(resp)
    }
