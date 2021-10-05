from datetime import datetime
from core_layer.model.submission_model import Submission
from sqlalchemy import Column, DateTime, String, ForeignKey, func
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean, Text
from .model_base import Base


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(String(36), primary_key=True)
    timestamp = Column(
        DateTime, server_default=func.now(), nullable=False)
    # e.g. published, flagged, cleared, removed
    status = Column(String(100), default="published")
    comment = Column(Text)
    is_review_comment = Column(Boolean)

    # Relationships
    user_id = Column(String(36), ForeignKey('users.id'))
    # many comments may refer to one user (bidirectional)
    user = relationship("User", back_populates="comments")

    # comments on this comment
    comments = relationship("Comment", back_populates="parent_comment")
    comment_sentiments = relationship(
        "CommentSentiment", back_populates="comment")
    issues = relationship("Issue", back_populates="comment")

    # Entity to which the comment refers to (only one of them may be filled)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="comments")
    submission_id = Column(String(36), ForeignKey('submissions.id'))
    submission = relationship("Submission", back_populates="comments")
    review_answer_id = Column(String(36), ForeignKey('review_answers.id'))
    review_anser = relationship("ReviewAnswer", back_populates="comments")
    parent_comment_id = Column(String(36), ForeignKey('comments.id'))
    # self-referential relationship
    parent_comment = relationship("Comment", remote_side=[id])

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.timestamp, datetime) else self.timestamp,
            'comment': self.comment,
            'is_review_comment': str(self.is_review_comment),
            'user': self.user.name if self.user else 'deleted'
        }


class CommentSentiment(Base):
    __tablename__ = 'comment_sentiments'
    id = Column(String(36), primary_key=True)
    type = Column(String(100))  # e.g. like, dislike, ...

    # Relationships
    user_id = Column(String(36), ForeignKey('users.id'))
    user = relationship("User", back_populates="comment_sentiments")
    comment_id = Column(String(36), ForeignKey('comments.id'))
    comment = relationship("Comment", back_populates="comment_sentiments")
