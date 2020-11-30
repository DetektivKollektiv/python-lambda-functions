from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from core_layer.model_base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    score = Column(Integer)
    experience_points = Column(Integer)
    level_id = Column(Integer, ForeignKey('levels.id'))

    level = relationship("Level", back_populates="users")
    reviews = relationship("Review", backref="user")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "score": self.score, "level": self.level_id, "level_description": self.level.description,
                "experience_points": self.experience_points}
