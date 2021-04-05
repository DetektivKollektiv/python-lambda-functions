from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base
from .review_model import Review
from .review_question_model import ReviewQuestion

from core_layer.model.review_question_model import question_option_pairs


class ReviewAnswer(Base):
    __tablename__ = 'review_answers'
    id = Column(String(36), primary_key=True)
    review_id = Column(String(36), ForeignKey(
        'reviews.id', ondelete='CASCADE', onupdate='CASCADE'))
    review_question_id = Column(String(36), ForeignKey(
        'review_questions.id', ondelete='SET NULL', onupdate='CASCADE'))
    answer = Column(Integer)
    comment = Column(Text)

    review_question = relationship(
        ReviewQuestion, back_populates="review_answers")

    review = relationship(Review, back_populates="review_answers")

    def to_dict(self):
        return {
            "id": self.id,
            "review_id": self.review_id,
            "review_question_id": self.review_question_id,
            "answer": self.answer,
            "comment": self.comment
        }

    def to_dict_with_questions_and_answers(self):
        return {
            "answer_id": self.id,
            "question_id": self.review_question_id,
            "content": self.review_question.content,
            "info": self.review_question.info,
            "hint": self.review_question.hint,
            "lower_bound": self.review_question.lower_bound,
            "upper_bound": self.review_question.upper_bound,
            "parent_question_id": self.review_question.parent_question_id,
            "max_children": self.review_question.max_children,
            "answer_value": self.answer,
            "comment": self.comment,
            "options": [option.to_dict() for option in self.review_question.options]
        }


class AnswerOption(Base):
    __tablename__ = 'answer_options'
    id = Column(String(36), primary_key=True)
    text = Column(Text)
    value = Column(Integer)
    tooltip = Column(Text)
    questions = relationship(
        "ReviewQuestion", secondary=question_option_pairs, back_populates="options")

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "value": self.value,
            "tooltip": self.tooltip
        }
