from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from core_layer.model_base import Base
from core_layer.model.review_answer_model import question_option_pairs


class ReviewQuestion(Base):
    __tablename__ = 'review_questions'
    id = Column(String(36), primary_key=True)
    content = Column(Text)
    info = Column(Text)

    parent_question_id = Column(String(36), ForeignKey(
        'review_questions.id', ondelete='CASCADE', onupdate='CASCADE'))
    lower_bound = Column(Integer)
    upper_bound = Column(Integer)
    max_children = Column(Integer)

    review_answers = relationship(
        "ReviewAnswer", back_populates="review_question")
    options = relationship("AnswerOption",
                           secondary=question_option_pairs,
                           back_populates="questions")

    parent_question = relationship("ReviewQuestion", remote_side=[
                                   id], back_populates="child_questions")
    child_questions = relationship(
        "ReviewQuestion", back_populates="parent_question")

    def to_dict(self):
        return {"id": self.id, "content": self.content, "info": self.info}

    def to_dict_with_answers(self):
        question = {"id": self.id, "content": self.content,
                    "info": self.info, "options": []}
        for option in self.options:
            question["options"].append(option.to_dict())
        return question
