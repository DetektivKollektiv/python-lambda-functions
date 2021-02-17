from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class Sentiment(Base):
    __tablename__ = 'sentiments'
    id = Column(String(36), primary_key=True)
    sentiment = Column(String(200))
    items = relationship("ItemSentiment")


class ItemSentiment(Base):
    __tablename__ = 'item_sentiments'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="sentiments")
    sentiment_id = Column(String(36), ForeignKey('sentiments.id'))
    sentiment = relationship("Sentiment", back_populates="items")
