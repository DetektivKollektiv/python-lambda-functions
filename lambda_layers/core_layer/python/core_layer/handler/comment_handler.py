from uuid import uuid4
import logging
from core_layer.db_handler import Session
from core_layer.model.comment_model import Comment


def create_comment(session, comment, user_id, parent_type, parent_id, is_review_comment=False, timestamp=None, status=None) -> Comment:
    """
    Creates comment

    Args:
        mandatory:
            comment (str)
            user_id (str)
            parent_type (str) needs to be one of: 'item', 'submission', 'review_answer', 'comment'
            parent_id (str) 
            session (Session)
        optional:
            is_test (bool)
            timestamp (DateTime)
            status (str)
    """

    comment_obj = Comment()

    comment_obj.id = str(uuid4())
    comment_obj.comment = comment
    comment_obj.user_id = user_id
    comment_obj.is_review_comment = is_review_comment
    if timestamp is not None:
        comment_obj.timestamp = timestamp
    comment_obj.status = status

    if parent_type == 'item':
        comment_obj.item_id = parent_id
    elif parent_type == 'submission':
        comment_obj.submission_id = parent_id
    elif parent_type == 'review_answer':
        comment_obj.review_answer_id = parent_id
    elif parent_type == 'review':
        comment_obj.review_id = parent_id
    elif parent_type == 'comment':
        comment_obj.parent_comment_id = parent_id
    else:
        logging.exception('unknown parent type.')

    session.add(comment_obj)
    session.commit()
    return comment_obj
