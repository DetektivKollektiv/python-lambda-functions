from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class Keyphrase(Base):
    __tablename__ = 'keyphrases'
    id = Column(String(36), primary_key=True)
    phrase = Column(String(100))
    items = relationship("ItemKeyphrase")

    def to_dict(self):
        return {"id": self.id, "phrase": self.phrase}


class ItemKeyphrase(Base):
    __tablename__ = 'item_keyphrases'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="keyphrases")
    keyphrase_id = Column(String(36), ForeignKey('keyphrases.id'))
    keyphrase = relationship("Keyphrase", back_populates="items")
