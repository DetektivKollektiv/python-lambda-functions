from core_layer.model.submission_model import Submission
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from .model_base import Base

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(String(36), primary_key = True)  
    timestamp = Column(DateTime)
    status = Column(String, default = "published") # e.g. published, flagged, cleared, removed
    comment = Column(String)

    # Relationships
    user_id = Column(String(36), ForeignKey('users.id'))
    user = relationship("User", back_populates = "comments") # many comments may refer to one user (bidirectional)

    comments = relationship("Comment", back_populates = "parent_comment") # comments on this comment
    comment_sentiments = relationship("CommentSentiment", back_populates = "comment")
    issues = relationship("Issue", back_populates = "comment")

    # Entity to which the comment refers to (only one of them may be filled)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates = "comments")
    submission_id = Column(String(36), ForeignKey('submissions.id'))
    submission = relationship("Submission", back_populates = "comments")
    review_answer_id = Column(String(36), ForeignKey('review_answers.id'))
    review_anser = relationship("ReviewAnswer", back_populates = "comments")
    parent_comment_id = Column(String(36), ForeignKey('comments.id'))
    parent_comment = relationship("Comment", remote_side = [id]) # self-referential relationship


class CommentSentiment(Base):
    __tablename__ = 'comment_sentiments'
    id = Column(String(36), primary_key = True)
    type = Column(String) # e.g. like, dislike, ...

    # Relationships
    user_id = Column(String(36), ForeignKey('users.id'))
    user = relationship("User", back_populates= "comment_sentiments")
    comment_id = Column(String(36), ForeignKey('comments.id'))
    comment = relationship("Comment", back_populates = "comment_sentiments")