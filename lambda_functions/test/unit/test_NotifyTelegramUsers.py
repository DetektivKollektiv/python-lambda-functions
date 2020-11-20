# import crud.operations as operations
# import crud.helper as helper
# from crud.model import User, Item, Submission
# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import relationship, backref, sessionmaker
# import test.unit.event_creator as event_creator
# from datetime import datetime
# import json
# import boto3
# from botocore.config import Config
# import test.unit.setup_scenarios as scenarios


# # This test uses the following secrets from the AWS secrets manager:
# # telegram_test_chat_id: telegram chat id of a user (uses an actual Telegram account)
# # mail: mail address of a user (uses detektivkollektic@gmail.com)
# # To override these values, uncomment the following lines and set the according strings:
# # TELEGRAM_CHAT_ID = "XXXXXXX" # you can find out your chat id by texting @chatid_echo_bot
# # RECIPIENT_MAIL = "XXXXXXX" # make sure the email address is verified in AWS SES as long as we are in Sandbox mode

# boto_session = boto3.session.Session()
# config = Config(read_timeout=2, connect_timeout=2)
# client = boto_session.client(
#     service_name='secretsmanager',
#     region_name='eu-central-1',
#     config=config
# )

# try:
#     TELEGRAM_CHAT_ID
# except NameError:
#     telegram_secret_name = 'telegram_test_chat_id'
#     get_telegram_secret = client.get_secret_value(
#         SecretId=telegram_secret_name
#     )
#     telegram_secret = get_telegram_secret['SecretString']
#     TELEGRAM_CHAT_ID = json.loads(telegram_secret)[telegram_secret_name]
#     assert(TELEGRAM_CHAT_ID is not None)

# try:
#     RECIPIENT_MAIL
# except NameError:
#     mail_secret_name = 'mail_test_address'
#     get_mail_secret = client.get_secret_value(
#         SecretId=mail_secret_name
#     )
#     mail_secret = get_mail_secret['SecretString']
#     RECIPIENT_MAIL = json.loads(mail_secret)[mail_secret_name]
#     assert(RECIPIENT_MAIL is not None)


# def test_closed_item_notification(monkeypatch):
#     monkeypatch.setenv("DBNAME", "Test")
#     monkeypatch.setenv("STAGE", "dev")
#     import app

#     session = operations.get_db_session(True, None)

#     session = scenarios.create_levels_junior_and_senior_detectives(session)

#     junior_detective1 = operations.get_user_by_id("1", True, session)
#     junior_detective2 = operations.get_user_by_id("2", True, session)
#     junior_detective3 = operations.get_user_by_id("3", True, session)
#     junior_detective4 = operations.get_user_by_id("4", True, session)

#     senior_detective1 = operations.get_user_by_id("11", True, session)
#     senior_detective2 = operations.get_user_by_id("12", True, session)
#     senior_detective3 = operations.get_user_by_id("13", True, session)
#     senior_detective4 = operations.get_user_by_id("14", True, session)

#     users = operations.get_all_users_db(True, session)
#     assert len(users) == 8

#     # Creating an item
#     item = Item()
#     item.content = "This item needs to be checked"
#     item = operations.create_item_db(item, True, session)

#     assert item.id is not None

#     # Creating more submissions for this item

#     submission = Submission()
#     submission.item_id = item.id
#     submission.telegram_id = TELEGRAM_CHAT_ID

#     submission2 = Submission()
#     submission2.item_id = item.id
#     submission2.mail = RECIPIENT_MAIL

#     submission = operations.create_submission_db(submission, True, session)
#     submission2 = operations.create_submission_db(submission2, True, session)

#     items = operations.get_all_items_db(True, session)
#     assert len(items) == 1

#     # Junior detectives accepting item
#     operations.accept_item_db(junior_detective1, item, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_1 == 3
#     assert item.in_progress_reviews_level_1 == 1

#     operations.accept_item_db(junior_detective2, item, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_1 == 3
#     assert item.in_progress_reviews_level_1 == 2

#     operations.accept_item_db(junior_detective3, item, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_1 == 3
#     assert item.in_progress_reviews_level_1 == 3

#     with pytest.raises(Exception):
#         operations.accept_item_db(junior_detective4, item, True, session)

#     # Senior detectives accepting item
#     operations.accept_item_db(senior_detective1, item, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_2 == 3
#     assert item.in_progress_reviews_level_2 == 1

#     operations.accept_item_db(senior_detective2, item, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_2 == 3
#     assert item.in_progress_reviews_level_2 == 2

#     operations.accept_item_db(senior_detective3, item, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_2 == 3
#     assert item.in_progress_reviews_level_2 == 3

#     with pytest.raises(Exception):
#         operations.accept_item_db(senior_detective4, item, True, session)

#     # Junior detectives reviewing item

#     review_event = event_creator.get_review_event(
#         item.id, junior_detective4.id, 1)
#     response = app.submit_review(review_event, None, True, session)
#     assert response['statusCode'] == 400

#     review_event = event_creator.get_review_event(
#         item.id, junior_detective1.id, 1)
#     app.submit_review(review_event, None, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_1 == 2
#     assert item.in_progress_reviews_level_1 == 2

#     review_event = event_creator.get_review_event(
#         item.id, junior_detective2.id, 1)
#     app.submit_review(review_event, None, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_1 == 1
#     assert item.in_progress_reviews_level_1 == 1

#     review_event = event_creator.get_review_event(
#         item.id, junior_detective3.id, 1)
#     app.submit_review(review_event, None, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_1 == 0
#     assert item.in_progress_reviews_level_1 == 0

#     # Senior detectives reviewing item

#     review_event = event_creator.get_review_event(
#         item.id, senior_detective4.id, 1)
#     response = app.submit_review(review_event, None, True, session)
#     assert response['statusCode'] == 400

#     review_event = event_creator.get_review_event(
#         item.id, senior_detective1.id, 1)
#     app.submit_review(review_event, None, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_2 == 2
#     assert item.in_progress_reviews_level_2 == 2

#     review_event = event_creator.get_review_event(
#         item.id, senior_detective2.id, 1)
#     app.submit_review(review_event, None, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_2 == 1
#     assert item.in_progress_reviews_level_2 == 1

#     review_event = event_creator.get_review_event(
#         item.id, senior_detective3.id, 1)
#     app.submit_review(review_event, None, True, session)
#     item = operations.get_item_by_id(item.id, True, session)
#     assert item.open_reviews_level_2 == 0
#     assert item.in_progress_reviews_level_2 == 0

#     assert item.status == "closed"
#     assert item.result_score == 1
