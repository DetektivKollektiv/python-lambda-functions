from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class URL(Base):
    __tablename__ = 'urls'
    id = Column(String(36), primary_key=True)
    url = Column(String(200))
    items = relationship("ItemURL")
    claimant_id = Column(String(36), ForeignKey('claimants.id'))
    claimant = relationship("Claimant", back_populates="url")
    unsafe = Column(String(50))


class ItemURL(Base):
    __tablename__ = 'item_urls'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="urls")
    url_id = Column(String(36), ForeignKey('urls.id'))
    url = relationship("URL", back_populates="items")
