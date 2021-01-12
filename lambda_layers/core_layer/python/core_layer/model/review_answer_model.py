from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class ReviewAnswer(Base):
    __tablename__ = 'review_answers'
    id = Column(String(36), primary_key=True)
    review_id = Column(String(36), ForeignKey(
        'reviews.id', ondelete='CASCADE', onupdate='CASCADE'))
    review_question_id = Column(String(36), ForeignKey(
        'review_questions.id', ondelete='CASCADE', onupdate='CASCADE'))
    answer = Column(Integer)
    comment = Column(Text)

    review_question = relationship(
        "ReviewQuestion", back_populates="review_answers")

    review = relationship("Review", back_populates="review_answers")

    def to_dict(self):
        return {"id": self.id, "review_id": self.review_id, "review_question_id": self.review_question_id,
                "answer": self.answer, "comment": self.comment}


question_option_pairs = Table('question_option_pairs', Base.metadata,
                              Column('question_id', String(36),
                                     ForeignKey('review_questions.id')),
                              Column('option_id', String(36),
                                     ForeignKey('answer_options.id'))
                              )


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
