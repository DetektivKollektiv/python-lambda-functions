import json
from ....tests.helper import event_creator, setup_scenarios
from core_layer.db_handler import Session
from core_layer.model.item_model import Item
from review_service.update_review import update_review
from ...get_open_items import get_open_items

from core_layer.handler import user_handler, item_handler, review_handler


class TestGetOpenItems:
    def test_get_open_items_for_user(self):

        with Session() as session:

            session = setup_scenarios.create_levels_junior_and_senior_detectives(session)
            session = setup_scenarios.create_questions(session)
            
            junior_detective1 = user_handler.get_user_by_id("1", session)            
            junior_detective2 = user_handler.get_user_by_id("2", session)
            junior_detective3 = user_handler.get_user_by_id("3", session)
            junior_detective4 = user_handler.get_user_by_id("4", session)
            junior_detective5 = user_handler.get_user_by_id("5", session)

            senior_detective1 = user_handler.get_user_by_id("11", session)
            
            # Creating 5 items

            item1 = Item()
            item1.content = "Item 1"
            item1.status = "open"
            item1.item_type_id = "Type1"
            item1 = item_handler.create_item(item1, session)
            
            item2 = Item()
            item2.content = "Item 2"
            item2.status = "open"
            item2.item_type_id = "Type1"
            item2 = item_handler.create_item(item2, session)

            item3 = Item()
            item3.content = "Item 3"
            item3.status = "open"
            item3.item_type_id = "Type1"
            item3 = item_handler.create_item(item3, session)

            item4 = Item()
            item4.content = "Item 4"
            item4.status = "open"
            item4.item_type_id = "Type1"
            item4 = item_handler.create_item(item4, session)

            item5 = Item()
            item5.content = "Item 5"
            item5.status = "open"
            item5.item_type_id = "Type1"
            item5 = item_handler.create_item(item5, session)

            items = item_handler.get_all_items(session)
            assert len(items) == 5
            
            open_items_for_senior = item_handler.get_open_items_for_user(senior_detective1, 5, session)['items']
            assert len(open_items_for_senior) == 5
            
            open_items_for_junior = item_handler.get_open_items_for_user(junior_detective1, 5, session)['items']
            assert len(open_items_for_junior) == 5
            
            # JuniorDetective 1 accepting item 1
            jr1 = review_handler.create_review(junior_detective1, item1, session)
            open_item_after_accept = item_handler.get_open_items_for_user(junior_detective1, 5, session)['items']
            assert len(open_item_after_accept) == 1
            
            item1 = item_handler.get_item_by_id(item1.id, session)
            assert item1.in_progress_reviews_level_1 == 1
            
            # Accepting event again should not create a new review
            review_handler.create_review(junior_detective1, item1, session)
            # app.create_review(accept_event, None, True, session)
            item1 = item_handler.get_item_by_id(item1.id, session)
            assert item1.in_progress_reviews_level_1 == 1
            
            # JuniorDetective 1 finishing review
            event = event_creator.get_review_event(jr1, item1.id, "in progress", jr1.user_id, 1)       
            response = update_review(event, None)
            assert response['statusCode'] == 200            
            event = event_creator.get_review_event(jr1, item1.id, "closed", jr1.user_id, 1)
            response = update_review(event, None)
            assert response['statusCode'] == 200           

            # For JuniorDetective1 only 4 cases should be available
            open_items_after_submission = item_handler.get_open_items_for_user(junior_detective1, 5, session)['items']
            assert len(open_items_after_submission) == 4
            
            open_items_limit_3 = item_handler.get_open_items_for_user(junior_detective1, 3, session)['items']
            assert len(open_items_limit_3) == 3

            open_items_after_other_review = item_handler.get_open_items_for_user(junior_detective4, 5, session)['items']
            assert len(open_items_after_other_review) == 5
            
            # 4 Junior Detectives reviewing Item 2

            jr1 = review_handler.create_review(junior_detective1, item2, session)            
            jr2 = review_handler.create_review(junior_detective2, item2, session)
            jr3 = review_handler.create_review(junior_detective3, item2, session)
            jr4 = review_handler.create_review(junior_detective4, item2, session)
            
            reviews = [jr1, jr2, jr3, jr4]
            for review in reviews:
                event = event_creator.get_review_event(
                    review, item2.id, "in progress", review.user_id, 1)
                response = update_review(event, None)
                assert response['statusCode'] == 200
                event = event_creator.get_review_event(
                    review, item2.id, "closed", review.user_id, 1)
                response = update_review(event, None)
                assert response['statusCode'] == 200
            
            # 4 Cases should be available for Detective 5
            open_items_after_other_review = item_handler.get_open_items_for_user(junior_detective5, 5, session)['items']
            assert len(open_items_after_other_review) == 4
            
            # 5 cases should be available for senior
            open_items_for_senior = item_handler.get_open_items_for_user(senior_detective1, 5, session)['items']
            assert len(open_items_for_senior) == 5
            
            # Senior detective accepting item 1
            sr1 = review_handler.create_review(senior_detective1, item1, session)

            open_item_after_accept = item_handler.get_open_items_for_user(senior_detective1, 5, session)['items']
            assert len(open_item_after_accept) == 1
            
            # Senior detective finishing review
            event = event_creator.get_review_event(sr1, item1.id, "in progress", sr1.user_id, 1)
            response = update_review(event, None)
            assert response['statusCode'] == 200
            event = event_creator.get_review_event(sr1, item1.id, "closed", sr1.user_id, 1)
            response = update_review(event, None)
            assert response['statusCode'] == 200
            
            # For SeniorDetective1 only 4 cases should be available
            open_items_after_submission = item_handler.get_open_items_for_user(senior_detective1, 5, session)['items']
            assert len(open_items_after_submission) == 4

            # SeniorDetective 1 accepting item 3
            sr1 = review_handler.create_review(senior_detective1, item3, session)
            open_item_after_accept = item_handler.get_open_items_for_user(senior_detective1, 5, session)['items']
            assert len(open_item_after_accept) == 1

            item3 = item_handler.get_item_by_id(item3.id, session)
            assert item3.in_progress_reviews_level_2 == 1
            
            # Accepting event again should not create a new review
            review_handler.create_review(senior_detective1, item3, session)
            item3 = item_handler.get_item_by_id(item3.id, session)
            assert item3.in_progress_reviews_level_2 == 1
            
            # SeniorDetective 1 finishing review
            event = event_creator.get_review_event(sr1, item3.id, "in progress", sr1.user_id, 1)
            response = update_review(event, None)
            assert response['statusCode'] == 200
            event = event_creator.get_review_event(sr1, item3.id, "closed", sr1.user_id, 1)
            response = update_review(event, None)
            assert response['statusCode'] == 200
            
            open_items_for_senior = item_handler.get_open_items_for_user(senior_detective1, 5, session)['items']
            assert len(open_items_for_senior) == 3

            event = {
                "requestContext": {
                    "identity": {
                        "cognitoAuthenticationProvider": "...CognitoSignIn:{}".format(senior_detective1.id)
                    }
                }
            }
            response = get_open_items(event, None)
            # assert 'is_open_review' in response['headers']
            # assert response['headers']['is_open_review'] == "False"
            body = json.loads(response['body'])
            assert 'is_open_review' in body
            assert body['is_open_review'] == False
            assert len(body['items']) == 3
