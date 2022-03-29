from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    score = Column(Integer, default=0)
    experience_points = Column(Integer, default=0)
    sign_up_timestamp = Column(DateTime, server_default=func.now())

    # Relationships
    level_id = Column(Integer, ForeignKey('levels.id'), default=1)
    level = relationship("Level", back_populates="users")
    reviews = relationship("Review", backref="user")
    comments = relationship("Comment", back_populates="user")
    comment_sentiments = relationship(
        "CommentSentiment", back_populates="user")
    # many user may belong to one mail
    mail_id = Column(String(36), ForeignKey('mails.id')) # adds a ForeignKey with the id of the mail
    mail = relationship('Mail', back_populates = 'users') # adds a 'virtual column' with a link to the mail table    

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "level": self.level_id,
            "level_description": self.level.description,
            "experience_points": self.experience_points,
            "sign_up_timestamp": str(self.sign_up_timestamp)
        }