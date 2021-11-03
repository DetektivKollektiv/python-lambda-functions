from core_layer.model.review_model import Review
from sqlalchemy import Table, Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .model_base import Base


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(String(36), primary_key=True)
    tag = Column(String(200))
    items = relationship("ItemTag")

    def to_dict(self):
        return {"id": self.id, "tag": self.tag}


class ItemTag(Base):
    __tablename__ = 'item_tags'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="tags")
    tag_id = Column(String(36), ForeignKey('tags.id'))
    tag = relationship("Tag", back_populates="items")
    review_id = Column(String(36), ForeignKey('reviews.id'))
    review = relationship("Review", back_populates="tags")
