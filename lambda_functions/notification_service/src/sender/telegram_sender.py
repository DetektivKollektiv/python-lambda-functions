import logging
from core_layer.handler.notification_template_handler import S3NotificationTemplateHandler
import requests
import os
import boto3
import json

from botocore.exceptions import ClientError

from notification_service.src.sender.notification_sender import NotificationSender

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TelegramNotificationError(Exception):
    pass


class TelegramSender(NotificationSender):
    def __init__(self, notification_template_handler: S3NotificationTemplateHandler) -> None:
        super().__init__(notification_template_handler)

        self._message_type = "telegram"

    def _send_notification_internal(self, telegram_id: str, replacements: dict = None):
        """Notifies a telegram user via their telegram_id (= chat_id).

        Parameters
        ----------
        telegram_id: string
            The telegram user's chat id

        replacements: dict (optional)
            Dictionary of replacements that should be replaced in the notification message and subject.
            Key: The placeholder in the message and subject
            Value: The value to replace the placeholder with

        """

        try:

            TELEGRAM_BOT_TOKEN = self._get_telegram_token()

            message = self._get_text('text', replacements)

            request_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={telegram_id}&parse_mode=Markdown&text={message}"

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

    def _get_telegram_token():
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
