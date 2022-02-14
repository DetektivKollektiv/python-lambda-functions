from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(String(36), primary_key=True)
    is_peer_review = Column(Boolean)
    belongs_to_good_pair = Column(Boolean)
    last_question_id = Column(String(36), ForeignKey(
        'review_questions.id', ondelete='SET NULL', onupdate='CASCADE'))
    user_id = Column(String(36), ForeignKey('users.id'))
    item_id = Column(String(36), ForeignKey('items.id',
                                            ondelete='CASCADE', onupdate='CASCADE'))
    start_timestamp = Column(DateTime, server_default=func.now())
    finish_timestamp = Column(DateTime)
    status = Column(String(100), default="in_progress")

    review_answers = relationship(
        "ReviewAnswer", back_populates="review", lazy="joined")
    item = relationship("Item", back_populates="reviews")
    last_question = relationship('ReviewQuestion')
    tags = relationship('ItemTag', back_populates="review", lazy="joined")
    comment = relationship('Comment', back_populates='review', uselist=False)

    def to_dict(self, with_questions_and_answers=False, with_user=False, with_tags=False):
        return_dict = {
            "id": self.id,
            "is_peer_review": self.is_peer_review,
            "belongs_to_good_pair": self.belongs_to_good_pair,
            "user_id": self.user_id,
            "start_timestamp": self.start_timestamp.isoformat(),
            "finish_timestamp": self.finish_timestamp.isoformat()
        }
        return_dict['comment'] = self.comment.comment if self.comment else None
        if with_questions_and_answers:
            return_dict['questions'] = [review_answer.to_dict_with_questions_and_answers()
                                        for review_answer in self.review_answers]
        if with_user:
            return_dict['user'] = self.user.name if self.user else None
        if with_tags:
            return_dict['tags'] = [
                item_tag.tag.tag for item_tag in self.tags] if self.tags else []
        return return_dict
