from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class Level(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    required_experience_points = Column(Integer)

    users = relationship("User", back_populates="level")
