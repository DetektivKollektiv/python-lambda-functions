from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base
from sqlalchemy.sql import func
from datetime import datetime
import collections


class Item(Base):
    __tablename__ = 'items'
    id = Column(String(36), primary_key=True)
    type = Column(String(36))
    content = Column(Text)
    language = Column(String(2))
    status = Column(String(36), default='unconfirmed')
    variance = Column(Float)
    result_score = Column(Float)
    open_reviews = Column(Integer, default=4)
    open_reviews_level_1 = Column(Integer, default=4)
    open_reviews_level_2 = Column(Integer, default=4)
    in_progress_reviews_level_1 = Column(Integer, default=0)
    in_progress_reviews_level_2 = Column(Integer, default=0)
    open_timestamp = Column(
        DateTime, server_default=func.now(), nullable=False)
    close_timestamp = Column(DateTime)
    verification_process_version = Column(Integer)

    item_type_id = Column(String(36), ForeignKey(
        'item_types.id', ondelete='SET NULL', onupdate='CASCADE'))

    submissions = relationship("Submission")
    factchecks = relationship("ExternalFactCheck")
    entities = relationship("ItemEntity")
    # One to Many Relation: one Item has many ItemTags
    tags = relationship("ItemTag")
    urls = relationship("ItemURL")
    sentiments = relationship("ItemSentiment")
    keyphrases = relationship("ItemKeyphrase")
    reviews = relationship("Review", back_populates="item", lazy="joined")
    review_pairs = relationship(
        "ReviewPair", back_populates="item", lazy="joined")
    item_type = relationship("ItemType", back_populates="items")
    comments = relationship("Comment", back_populates="item")

    def to_dict(self, with_tags=False, include_type=False, with_urls=False, with_reviews=False, with_comments=False, with_warnings=False):
        item_dict = {
            "id": self.id,
            "item_type_id": self.item_type_id,
            "content": self.content,
            "language": self.language,
            "status": self.status,
            "variance": self.variance,
            "result_score": self.result_score,
            "open_reviews_level_1": self.open_reviews_level_1,
            "open_reviews_level_2": self.open_reviews_level_2,
            "open_reviews": self.open_reviews,
            "in_progress_reviews_level_1": self.in_progress_reviews_level_1,
            "in_progress_reviews_level_2": self.in_progress_reviews_level_2,
            "open_timestamp": self.open_timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.open_timestamp, datetime) else self.open_timestamp,
            "close_timestamp": self.close_timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.close_timestamp, datetime) else self.close_timestamp
        }

        if with_tags:
            tags_list = []
            for item_tag in self.tags:
                tags_list.append(item_tag.tag.tag)
            sorted_list = collections.Counter(tags_list).most_common()
            item_dict["tags"] = [entry[0] for entry in sorted_list]

        if with_urls:
            url_list = []
            for item_url in self.urls:
                url_dict = {
                    'url': item_url.url.url,
                    'is_safe': item_url.url.unsafe is None
                }
                url_list.append(url_dict)
            item_dict["urls"] = url_list

        if include_type and self.item_type:
            item_dict["item_type"] = self.item_type.to_dict()

        # Provide a list of all reviews on the item AND a separate list of all users including their lvl description
        if with_reviews:
            item_dict['reviews'] = []
            item_dict['users'] = []
            for review in self.reviews:
                item_dict['reviews'].append(review.to_dict(True, True))
                if review.user and review.user.level:
                    item_dict['users'].append(
                        {'username': review.user.name, 'level_description': review.user.level.description})
                else:
                    item_dict['users'].append(None)

        if with_comments:
            item_dict['review_comments'] = []
            for review in self.reviews:
                if review.comment is not None:
                    item_dict['review_comments'].append(
                        review.comment.to_dict())
            item_dict['discussion_comments'] = []
            for comment in self.comments:
                item_dict['discussion_comments'].append(comment.to_dict())

        if with_warnings:
            questions_with_warning_tags = []
            answer_dict = {}
            for review in self.reviews:
                for answer in review.review_answers:
                    if answer.answer is not None:
                        if answer.review_question_id not in answer_dict:
                            answer_dict[answer.review_question_id] = {
                                'question': answer.review_question,
                                'answers': [answer.answer]
                            }
                        else:
                            answer_dict[answer.review_question_id]['answers'].append(
                                answer.answer)
            for key in answer_dict:
                answers = answer_dict[key]['answers']
                question = answer_dict[key]['question']
                if len(answers) > 2:
                    if sum(answers) / len(answers) <= 2:
                        if question not in questions_with_warning_tags:
                            questions_with_warning_tags.append(question)
            item_dict['warning_tags'] = []
            for q in questions_with_warning_tags:
                item_dict['warning_tags'].append(
                    {'text': q.warning_tag, 'icon': q.warning_tag_icon_code})
        return item_dict
