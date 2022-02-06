# External imports
from uuid import uuid4
import logging, os
# Helper imports
from core_layer import helper
# Model imports
from core_layer.model.mail_model import Mail

from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from notification_service.src.sender.mail_sender import MailSender
from core_layer.responses import InternalError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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


def get_mail_by_mail_id(mail_id, session):
    """
    Returns Mail object by given mail_id

    Parameters
    ----------
    mail_id: string
    """
    
    mail = session.query(Mail).filter(Mail.id == mail_id).first()
    return mail


def get_mail_by_user_id(user_id, session):
    """
    Returns Mail object by given user_id

    Parameters
    ----------
    user_id: string
    """
    
    mail = session.query(Mail).filter(Mail.user_id == user_id).first()
    return mail


def send_confirmation_mail(mail):

    stage = os.environ['STAGE']
    if stage == 'prod':
        confirmation_link = 'https://api.codetekt.org/user_service/mails/{}/confirm'.format(
            mail.id)
    else:
        confirmation_link = 'https://api.{}.codetekt.org/user_service/mails/{}/confirm'.format(
            stage, mail.id)

    notification_template_handler = NotificationTemplateHandler()
    mail_sender = MailSender(notification_template_handler)

    parameters = dict(mail_confirmation_link = confirmation_link)

    try: 
        mail_sender.send_notification("mail_confirmation", mail = mail.email, replacements = parameters)
        logger.info("Confirmation email sent for mail with ID: {}".format(mail.id))

    except Exception as e:
        return InternalError(f"Error sending confirmation mail with mail_id {mail.id}", e, add_cors_headers = False).to_json_string()