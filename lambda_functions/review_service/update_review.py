from core_layer.event_publisher import EventPublisher
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import user_handler, review_handler, review_answer_handler, comment_handler, tag_handler
from core_layer import responses
import logging
import json
import traceback


def update_review(event, context):
    """Updates an existing review

    Args:
        event: AWS API Gateway event
        context ([type]): [description].

    Returns
    ------
    - Status code 200, 400, 404 or 500 (Created)
    - The updated review
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Update Review", event, logger)

    try:
        user_id = helper.cognito_id_from_event(event)
        body = json.loads(event['body']) if isinstance(
            event['body'], str) else event['body']
    except:
        return responses.BadRequest(event, "Malformed request. Please provide a valid request.").to_json_string()

    if 'id' not in body:
        return responses.BadRequest(event, "Malformed request. Please provide a review id.").to_json_string()

    with Session() as session:

        try:
            review = review_handler.get_review_by_id(body['id'], session)
        except:
            return responses.NotFound(event, "No review found.").to_json_string()

        try:
            user = user_handler.get_user_by_id(user_id, session)
        except:
            return responses.NotFound(event, "No user found.").to_json_string()

        if review.user_id != user.id:
            return responses.Forbidden(event).to_json_string()
        # If review is set closed
        if 'status' in body and body['status'] == 'closed':
            try:
                review = review_handler.close_review(review, session)

                if review.item.status == 'closed':
                    EventPublisher().publish_event('codetekt.review_service',
                                                   'item_closed', {'item_id': review.item.id})
                return responses.Success(event, review.to_dict(with_questions_and_answers=True, with_tags=True)).to_json_string()
            except:
                return helper.get_text_response(500, "Internal server error. Stacktrace: {}".format(traceback.format_exc()), event)

        # If answers are appended
        if 'questions' in body:
            if not isinstance(body['questions'], list):
                return responses.BadRequest(event, "Malformed request. Please provide a valid request.").to_json_string()
            for question in body['questions']:
                if 'answer_value' in question:
                    answer_value = question['answer_value']
                else:
                    return responses.BadRequest(event, "Malformed request. Please provide a valid request.").to_json_string()

                if answer_value is not None:
                    # Check if conditionality is met
                    if question['parent_question_id'] is not None:
                        for q in body['questions']:
                            if q['question_id'] == question['parent_question_id']:
                                parent_question = q
                        if parent_question['answer_value'] > question['upper_bound'] or parent_question['answer_value'] < question['lower_bound']:
                            return responses.BadRequest(event, "Bad request. Please adhere to conditionality of questions.").to_json_string()
                    # Update answer in db
                    try:
                        review_answer_handler.set_answer_value(
                            question['answer_id'], question['answer_value'], session)
                    except Exception as e:
                        return responses.InternalError(event, exception=e).to_json_string()

        # Save qualitative_comment
        if 'comment' in body:
            if body['comment']:
                if review.comment is None:
                    try:
                        comment_handler.create_comment(session,
                                                       comment=body['comment'],
                                                       user_id=user_id,
                                                       parent_type='review',
                                                       parent_id=review.id,
                                                       is_review_comment=True
                                                       )
                    except Exception as e:
                        return responses.InternalError(event, "Could not create comment for item", e).to_json_string()
                elif review.comment.comment != body['comment']:
                    review.comment.comment = body['comment']
                    session.merge(review)

        if 'tags' in body:
            if isinstance(body['tags'], list) and len(body['tags']) > 0:
                try:
                    db_tags = [
                        item_tag.tag.tag for item_tag in tag_handler.get_item_tags_by_review_id(review.id, session)]
                    tags_to_add = list(set(body['tags']) - set(db_tags))
                    tags_to_delete = list(set(db_tags) - set(body['tags']))

                    for tag in tags_to_add:
                        tag_handler.store_tag_for_item(
                            review.item_id, tag, session, review.id)

                    for tag in tags_to_delete:
                        tag_handler.delete_itemtag_by_tag_and_review_id(
                            tag, review.id, session)
                except Exception as e:
                    return responses.InternalError(event, "Could not create tags for item", e).to_json_string()
        return responses.Success(event, json.dumps(review.to_dict(with_questions_and_answers=True, with_tags=True))).to_json_string()
