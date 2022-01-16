# External imports
from uuid import uuid4
import boto3, io, logging, os
# Helper imports
from core_layer import helper
# Model imports
from core_layer.model.mail_model import Mail


def create_mail(mail, session):
    """
    Inserts a new mail address into the database

    Parameters
    ----------
    mail: Mail object
    """

    mail.id = str(uuid4())
    mail.timestamp = helper.get_date_time_now()

    session.add(mail)
    session.commit()

    return mail


def get_mail_by_email_address(email, session):
    """
    Returns Mail object by given email address

    Parameters
    ----------
    email: string
    """
    
    mail = session.query(Mail).filter(Mail.email == email).first()
    return mail


def send_confirmation_mail(mail):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stage = os.environ['STAGE']
    if stage == 'prod':
        confirmation_link = 'https://api.codetekt.org/user_service/mails/{}/confirm'.format(
            mail.id)
    else:
        confirmation_link = 'https://api.{}.codetekt.org/user_service/mails/{}/confirm'.format(
            stage, mail.id)

    recipient = mail.email
    sender = "codetekt <no-reply@codetekt.org>"
    subject = 'Bestätige deine Mail-Adresse'

    body_text = "Bitte bestätige deine Mailadresse durch Klick auf folgenden Link {}".format(confirmation_link)
    body_html = io.open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..', 'lambda_functions/user_service/resources',
                                     'confirmation_file_body.html')), mode='r', encoding='utf-8').read().format(confirmation_link)

    charset = "UTF-8"
    client = boto3.client('ses', region_name = 'eu-central-1')
    try:
        response = client.send_email(
            Destination = {
                'ToAddresses': [
                    recipient,
                ],
            },
            Message = {
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source = sender,
        )
        logger.info("Confirmation email sent for mail with ID: {}. SES Message ID: {}".format(
            mail.id, response['MessageId']))

    except ClientError as e:
        logging.exception("Could not send confirmation mail for mail with ID: {}. SNS Error: {}".format(
            mail.id, e.response['Error']['Message']))
        pass