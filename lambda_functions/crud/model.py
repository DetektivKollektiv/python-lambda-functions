from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'
    id = Column(String, primary_key=True)
    content = Column(String)
    language = Column(String)
