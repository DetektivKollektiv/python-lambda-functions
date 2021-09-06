from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base

question_option_pairs = Table('question_option_pairs', Base.metadata,
                              Column('question_id', String(36),
                                     ForeignKey('review_questions.id', ondelete='SET NULL', onupdate='CASCADE')),
                              Column('option_id', String(36),
                                     ForeignKey('answer_options.id', ondelete='SET NULL', onupdate='CASCADE'))
                              )


class ReviewQuestion(Base):
    __tablename__ = 'review_questions'
    id = Column(String(36), primary_key=True)
    content = Column(Text)
    info = Column(Text)
    hint = Column(Text)

    parent_question_id = Column(String(36), ForeignKey(
        'review_questions.id', ondelete='CASCADE', onupdate='CASCADE'))
    lower_bound = Column(Integer)
    upper_bound = Column(Integer)
    max_children = Column(Integer)
    warning_tag = Column(String)

    item_type_id = Column(String(36), ForeignKey(
        'item_types.id', ondelete='SET NULL', onupdate='CASCADE'))

    review_answers = relationship(
        "ReviewAnswer", back_populates="review_question")
    options = relationship("AnswerOption",
                           secondary=question_option_pairs,
                           back_populates="questions")

    parent_question = relationship("ReviewQuestion", remote_side=[
                                   id], back_populates="child_questions")
    child_questions = relationship(
        "ReviewQuestion", back_populates="parent_question")

    item_type = relationship("ItemType", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "info": self.info,
            "hint": self.hint
        }

    def to_dict_with_answers(self):
        return {
            "id": self.id,
            "content": self.content,
            "info": self.info,
            "hint": self.hint,
            "options": [option.to_dict() for option in self.options]
        }
