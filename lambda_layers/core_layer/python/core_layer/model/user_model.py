from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    score = Column(Integer)
    experience_points = Column(Integer)
    level_id = Column(Integer, ForeignKey('levels.id'))
    sign_up_timestamp = Column(DateTime, server_default=func.now())

    level = relationship("Level", back_populates="users")
    reviews = relationship("Review", backref="user")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "level": self.level_id,
            "level_description": self.level.description,
            "experience_points": self.experience_points,
            "sign_up_timestamp": self.sign_up_timestamp
        }
