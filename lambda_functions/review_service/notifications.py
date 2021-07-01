# External imports
import os
import requests
import json
import logging
import boto3
from botocore.exceptions import ClientError

# Helper imports
from core_layer.db_handler import Session, update_object

# Handler imports
from core_layer.handler import submission_handler


# Set codetekt email address here (displayed name <mail address>)
SENDER = "codetekt <no-reply@codetekt.org>"


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
    client = session.client(
        service_name='secretsmanager',
        region_name='eu-central-1'
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
        logging.exception("Could not get telegram bot token from the secrets manager. Secrets manager error: {}".format(
            e.response['Error']['Code']))
        raise TelegramNotificationError


def notify_users(session, item):
    """Notify user(s) about a closed item.

    Parameters
    ----------
    session: session
        The session
    item: Item
        The closed item
    """

    # TODO: This implementation is not ideal: 1.55 is rounded to 1.5. However, 1.56 is correctly rounded to 1.6.
    rating = round(item.result_score, 1)
    rating_text = "nicht vertrauenswürdig"
    if 2 <= rating < 3:
        rating_text = "eher nicht vertrauenswürdig"
    if 3 <= rating < 3.5:
        rating_text = "eher vertrauenswürdig"
    if rating >= 3.5:
        rating_text = "vertrauenswürdig"

    # get all submissions for the item
    submissions = submission_handler.get_submissions_by_item_id(item.id, session)

    notifications_successful = True

    for submission in submissions:
        if submission.telegram_id:
            try:
                notify_telegram_user(submission.telegram_id, item, rating, rating_text)
                submission.telegram_id = None
            except Exception:
                notifications_successful = False

        if submission.mail:
            if submission.status == 'confirmed':
                try:
                    notify_mail_user(submission.mail, item,
                                     rating, rating_text)
                    submission.mail = None
                except Exception:
                    notifications_successful = False

    if notifications_successful:
        logger.info(
            "User(s) notified. Check logs to see if mail and/or telegram notifications were successful.")
        update_object(submission, session)
    else:
        logger.exception(
            "An error occurred during closed item user notification. Please check logs.")


def notify_telegram_user(telegram_id, item, rating, rating_text):
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
        text_rating = "Der Vertrauensindex beträgt *{} von 4*. Damit ist dein Fall *{}*. Was bedeutet das?\n\n".format(
            rating, rating_text)
        text_legend = "1: nicht vertrauenswürdig\n2: eher nicht vertrauenswürdig\n3: eher vertrauenswürdig\n4: vertrauenswürdig\n\n"
        text_archive = "Mehr Details zu deinem Fall findest du in unserem [Archiv](https://qa.codetekt.org/archive).\n\n"
        text_thanks = "Wir danken dir für deine Unterstützung in unserer Mission für mehr Transparenz!\n\n"
        text_case = "Dein Fall lautete: \n{}".format(item.content)

        message = text_solved + text_rating + text_legend + \
            text_archive + text_thanks + text_case

        request_url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}".format(
            TELEGRAM_BOT_TOKEN, telegram_id, message)
        notify_user = requests.get(request_url)
        if notify_user.ok == True:
            logger.info("Telegram user notification request sent. Response: {}".format(
                notify_user.json()))
        else:
            raise TelegramNotificationError

    except Exception:
        logging.exception(
            "Could not notify telegram user with chat id {} about closed item.".format(telegram_id))
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
                 "Der Vertrauensindex beträgt {}. Damit ist dein Fall {}".format(
                     rating, rating_text)
                 )

    # The HTML body of the email
    BODY_HTML = """<html>
    <p>&nbsp;</p>
    <p><a href="http://codetekt.org/"> <img style="display: block; margin-left: auto; margin-right: auto;" src="https://codetekt-logo.s3.eu-central-1.amazonaws.com/codetekt_V2_rgb%404x.png" alt="codetekt" width="300" /> </a></p>
    <h1 style="color: #fac800; text-align: center;">Dein Fall wurde gel&ouml;st!</h1>
    <p>Hi! Unsere Community hat deinen Fall gel&ouml;st.</p>
    <h2>Der Vertrauensindex betr&auml;gt <strong>{} von 4</strong>. Damit ist dein Fall <strong>{}</strong>.</h2>
    <p>Was bedeutet das?</p>
    <div style="width: inherit; max-width: 400px; background-color: #c62828; padding: 10px 15px 10px 15px; border-radius: 5px;">1 - 2: nicht vertrauensw&uuml;rdig</div>
    <div style="width: inherit; max-width: 400px; background-color: #e57373; padding: 10px 15px 10px 15px; border-radius: 5px;">2 - 3: eher nicht vertrauensw&uuml;rdig</div>
    <div style="width: inherit; max-width: 400px; background-color: #66bb6a; padding: 10px 15px 10px 15px; border-radius: 5px;">3 - 3,5: eher vertrauensw&uuml;rdig</div>
    <div style="width: inherit; max-width: 400px; background-color: #1b5e20; padding: 10px 15px 10px 15px; border-radius: 5px;">3,5 - 4: vertrauensw&uuml;rdig</div>
    <p>Mehr Details zu deinem Fall findest du in unserem <a href="https://codetekt.org/archive?id={}">Archiv</a>.<br /><br />Wir danken dir f&uuml;r deine Unterst&uuml;tzung in unserer Mission f&uuml;r mehr Transparenz!</p>
    <p>Dein Fall lautete: <br />{}</p>
    <p>Antworten auf diese Mail werden nicht gelesen.</p>
    </html>
    """.format(rating, rating_text, item.id, item.content)

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
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
        logger.info("Notification email sent to {}. SES Message ID: {}".format(
            mail, response['MessageId']))
    except ClientError as e:
        logging.exception("Could not send mail notification to email address {}. SNS Error: {}".format(
            mail, e.response['Error']['Message']))
        raise EmailNotificationError
