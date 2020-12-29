from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class ItemType(Base):
    __tablename__ = 'item_types'
    id = Column(String(36), primary_key=True)
    name = Column(Text)

    items = relationship("Item")
    questions = relationship("ReviewQuestion")

    def to_dict(self):
        return {"id": self.id, "name": self.name}
