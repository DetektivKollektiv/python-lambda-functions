import os 
import requests
import json
import logging
import boto3
import base64
from botocore.exceptions import ClientError
from botocore.config import Config

from . import operations, helper

# Set DetektivKollektiv email address here (displayed name <mail address>)
SENDER = "DetektivKollektiv <detektivkollektiv@gmail.com>"

class TelegramNotificationError(Exception):
    pass

class EmailNotificationError(Exception):
    pass

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_telegram_token():
    """Gets the telegram bot token for the respective stage (dev/qa/prod) from the secrets manager.

    Parameters
    ----------
    is_test: boolean
        If this method is called from a test
    secret_name: string
        The name of the telegram bot token in the secrets manager
    """
    
    secret_name = "telegram_bot_token_{}".format(os.environ['STAGE'])

    # Create a Secrets Manager client
    session = boto3.session.Session()
    config = Config(read_timeout=2, connect_timeout=2)
    client = session.client(
        service_name='secretsmanager',
        region_name='eu-central-1',
        config=config
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

        print(get_secret_value_response)

        # Decrypts secret using the associated KMS CMK.
        secret = get_secret_value_response['SecretString']
        telegram_bot_token = json.loads(secret)[secret_name]
        
        return telegram_bot_token
        
    except ClientError as e:
        logging.exception("Could not get telegram bot token from the secrets manager. Secrets manager error: {}".format(e.response['Error']['Code']))
        raise TelegramNotificationError

def notify_users(is_test, session, item):
    """Notify telegram user(s) about a closed item.

    Parameters
    ----------
    is_test: boolean
        If this method is called from a test
    session: session
        The session
    item: Item
        The closed item
    """

    if session == None:
        session = operations.get_db_session(False, None)
    
    rating = round(item.result_score, 1) # TODO: This implementation is not ideal: 1.55 is rounded to 1.5. However, 1.56 is correctly rounded to 1.6.
    rating_text = "nicht vertrauenswürdig"
    if 1.5 <= rating < 2.5:
        rating_text = "eher nicht vertrauenswürdig"
    if 2.5 <= rating < 3.5:
        rating_text = "eher vertrauenswürdig"
    if rating >= 3.5: 
        rating_text = "vertrauenswürdig"

    # get all submissions for the item
    submissions = operations.get_submissions_by_item_id(item.id, is_test, session)

    notifications_successful = True

    for submission in submissions:
        if submission.telegram_id:
            try:
                notify_telegram_user(is_test, submission.telegram_id, item, rating, rating_text)
            except Exception:
                notifications_successful = False

        if submission.mail:
            try:
                notify_mail_user(submission.mail, item, rating, rating_text)
            except Exception:
                notifications_successful = False

    if notifications_successful:
        logger.info("User(s) notified. Check logs to see if mail and/or telegram notifications were successful.")
    else:
        logger.exception("An error occurred during closed item user notification. Please check logs.")


def notify_telegram_user(is_test, telegram_id, item, rating, rating_text):
    """Notifies a telegram user via their telegram_id (= chat_id).

    Parameters
    ----------
    telegram_id: string
        The telegram user's chat id
    item: Item
        The closed item
    rating: float 
        The item's result score, rounded to 2 decimal places
    rating_text: 
        The rating in textual form
    """

    try:

        TELEGRAM_BOT_TOKEN = get_telegram_token()

        text_solved = "Dein Fall wurde gelöst! "
        text_rating = "Der Vertrauensindex beträgt *{} von 4*. Damit ist dein Fall *{}*. Was bedeutet das?\n\n".format(rating, rating_text)
        text_legend = "1: nicht vertrauenswürdig\n2: eher nicht vertrauenswürdig\n3: eher vertrauenswürdig\n4: vertrauenswürdig\n\n"
        text_archive = "Mehr Details zu deinem Fall findest du in unserem [Archiv](https://qa.detective-collective.org/archive).\n\n"
        text_thanks = "Wir danken dir für deine Unterstützung in unserer Mission für mehr Transparenz!\n\n"
        text_case = "Dein Fall lautete: \n{}".format(item.content)

        message = text_solved + text_rating + text_legend + text_archive + text_thanks + text_case
                        
        request_url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}".format(TELEGRAM_BOT_TOKEN, telegram_id, message)
        notify_user = requests.get(request_url, timeout=5)
        if notify_user.ok == True:
            logger.info("Telegram user notification request sent. Response: {}".format(notify_user.json()))
        else:
            raise TelegramNotificationError

    except Exception:
        logging.exception("Could not notify telegram user with chat id {} about closed item.".format(telegram_id))
        raise TelegramNotificationError


def notify_mail_user(mail, item, rating, rating_text):
    """Notifies an email user via their mail.

    Parameters
    ----------
    mail: string
        The user's email address
    item: Item
        The closed item
    rating: float 
        The item's result score, rounded to 2 decimal places
    rating_text: 
        The rating in textual form
    """

    RECIPIENT = mail

    AWS_REGION = "eu-central-1"

    # The subject line for the email
    SUBJECT = "Dein Fall wurde gelöst!"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Unsere Detektiv*innen haben deinen Fall gelöst.\r\n"
                "Der Vertrauensindex beträgt {}. Damit ist dein Fall {}".format(rating, rating_text)
                )
                
    # The HTML body of the email
    BODY_HTML = """<html>
    <head><title>Dein Fall wurde gelöst!</title></head>
    <body>
    <a href="http://detektivkollektiv.de/">
        <img src="http://detektivkollektiv.de/wp-content/uploads/2020/07/cropped-Zeichenfla%CC%88che-1-Kopie-2.png" alt="DetektivKollektiv" width="300">
    </a>
    <h1 style="color: #ffcc00;">Dein Fall wurde gelöst!</h1>
    <p>Hi! Unsere Detektiv*innen haben deinen Fall gelöst.</p>
    <p>Der Vertrauensindex beträgt <b>{} von 4</b>. Damit ist dein Fall <b>{}</b>.</p>
    <p>Was bedeutet das?</p>
    <div style="width: inherit; max-width: 400px; background-color: #ffcc00; padding: 10px 15px 10px 15px; border-radius: 5px;">
    1: nicht vertrauenswürdig<br>
    2: eher nicht vertrauenswürdig<br>
    3: eher vertrauenswürdig<br>
    4: vertrauenswürdig
    </div>
    <p>
    Mehr Details zu deinem Fall findest du in unserem <a href="https://qa.detective-collective.org/archive">Archiv</a>.<br><br>
    Wir danken dir für deine Unterstützung in unserer Mission für mehr Transparenz!
    </p>
    <p>
    Dein Fall lautete: <br>
    {}
    </p>
    </body>
    </html>
    """.format(rating, rating_text, item.content)

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
        logger.info("Notification email sent to {}. SES Message ID: {}".format(mail, response['MessageId']))
    except ClientError as e:
        logging.exception("Could not send mail notification to email address {}. SNS Error: {}".format(mail, e.response['Error']['Message']))
        raise EmailNotificationError