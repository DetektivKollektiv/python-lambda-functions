import requests
import json
import logging

from . import operations, helper

# Set telegram bot token of 'Derrick' here
TELEGRAM_BOT_TOKEN = '1344994044:AAFjEb6OrJV_EmpR_DBhFPSsNvNexnSEmXk'
# TELEGRAM_BOT_TOKEN = '1kk44994044:AAFjEb6OrJV_EmpR_DBhFPSsNvNexnSEmXk'

class TelegramNotificationError(Exception):
    pass

def notify_telegram_users(is_test, session, item):
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

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if session == None:
        session = operations.get_db_session(False, None)

    # get all submissions for the item
    submissions = operations.get_submissions_by_item_id(item.id, is_test, session)

    mail_users = []
    telegram_users = []

    for submission in submissions:
        if submission.mail:
            mail_users.append(submission.mail)
        if submission.telegram_id:
            telegram_users.append(submission.telegram_id)

            # Notify telegram user(s)

            try:           

                rating = round(item.result_score, 1) # TODO: This implementation is not ideal: 1.55 is rounded to 1.5. However, 1.56 is correctly rounded to 1.6.
                rating_text = "nicht vertrauenswürdig"
                if 1.5 <= rating < 2.5:
                    rating_text = "eher nicht vertrauenswürdig"
                if 2.5 <= rating < 3.5:
                    rating_text = "eher vertrauenswürdig"
                if rating >= 3.5: 
                    rating_text = "vertrauenswürdig"

                message_part_1 = "Hi, Derrick hier. Ich habe Neuigkeiten zu deinem eingereichten Fall!\n\n"
                message_part_2 = "Unsere Detektiv\\*innen haben dem Fall einen Vertrauensindex von *{} von 4 ({})* gegeben. ".format(rating, rating_text)
                message_part_3 = "Mehr Details findest du im [Archiv](https://qa.detective-collective.org/archive).\n\n"
                message_part_4 = "Dein Fall lautete: \n{}".format(item.content)

                message = message_part_1 + message_part_2 + message_part_3 + message_part_4
                                
                request_url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}".format(TELEGRAM_BOT_TOKEN, submission.telegram_id, message)
                notify_user = requests.get(request_url, timeout=5)
                logger.info("Telegram user notification request sent. Response: {}".format(notify_user.json()))
                if notify_user.ok == False:
                    raise TelegramNotificationError
                
                logger.info("Item: {}; Mail users to notify: {}; Telegram users notified: {}".format(json.dumps(item.to_dict()), json.dumps(mail_users), json.dumps(telegram_users)))
            
            except Exception as e:
                raise TelegramNotificationError("Could not notify telegram users about closed item. Error: {}".format(e))