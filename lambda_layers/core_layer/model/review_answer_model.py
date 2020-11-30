from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from core_layer.model_base import Base


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
