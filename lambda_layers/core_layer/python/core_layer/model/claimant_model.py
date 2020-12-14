from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class Claimant(Base):
    __tablename__ = 'claimants'
    id = Column(String(36), primary_key=True)
    claimant = Column(String(200))
    url = relationship("URL")
