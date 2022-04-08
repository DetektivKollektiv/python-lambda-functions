# External imports
from uuid import uuid4
from datetime import datetime
import logging, os
# Model imports
from core_layer.model.mail_model import Mail
from core_layer.model.user_model import User

from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from notification_service.src.sender.mail_sender import MailSender

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
    mail.timestamp = datetime.now()

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
    
    mail = session.query(User).filter(User.id == user_id).first().mail
    return mail


def get_confirmation_link(mail_id):
    """
    Returns mail confirmation link by by given mail_id

    Parameters
    ----------
    mail_id: string
    """

    stage = os.environ['STAGE']
    if stage == 'prod':
        confirmation_link = f'https://api.codetekt.org/user_service/mails/{mail_id}/confirm'
    else:
        confirmation_link = f'https://api.{stage}.codetekt.org/user_service/mails/{mail_id}/confirm'

    return confirmation_link


def get_unsubscribe_link(mail_id):
    """
    Returns mail confirmation link by by given mail_id

    Parameters
    ----------
    mail_id: string
    """

    stage = os.environ['STAGE']
    if stage == 'prod':
        unsubscribe_link = f'https://api.codetekt.org/user_service/mails/{mail_id}/unsubscribe'
    else:
        unsubscribe_link = f'https://api.{stage}.codetekt.org/user_service/mails/{mail_id}/unsubscribe'

    return unsubscribe_link


def send_confirmation_mail(mail):

    notification_template_handler = NotificationTemplateHandler()
    mail_sender = MailSender(notification_template_handler)

    parameters = dict(mail_confirmation_link = get_confirmation_link(mail.id))

    try: 
        mail_sender.send_notification("mail_confirmation", mail = mail.email, replacements = parameters)
        logger.info(f"Confirmation email sent for mail with ID: {mail.id}")

    except:
        logger.info(f"Error sending confirmation mail with ID: {mail.id}")