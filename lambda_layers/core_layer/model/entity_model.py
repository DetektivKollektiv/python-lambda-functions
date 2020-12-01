from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from core_layer.model_base import Base


class Entity(Base):
    __tablename__ = 'entities'
    id = Column(String(36), primary_key=True)
    entity = Column(String(200))
    items = relationship("ItemEntity")

    def to_dict(self):
        return {"id": self.id, "entity": self.entity}


class ItemEntity(Base):
    __tablename__ = 'item_entities'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="entities")
    entity_id = Column(String(36), ForeignKey('entities.id'))
    entity = relationship("Entity", back_populates="items")
