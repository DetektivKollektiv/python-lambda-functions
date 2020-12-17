from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class FactChecking_Organization(Base):
    __tablename__ = 'factchecking_organizations'
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    counter_trustworthy = Column(Integer)
    counter_not_trustworthy = Column(Integer)
    factchecks = relationship("ExternalFactCheck")
