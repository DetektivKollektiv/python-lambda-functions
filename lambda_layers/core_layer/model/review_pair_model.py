from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from core_layer.model_base import Base


class ReviewPair(Base):
    __tablename__ = 'review_pairs'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    junior_review_id = Column(String(36), ForeignKey('reviews.id'))
    senior_review_id = Column(String(36), ForeignKey('reviews.id'))
    is_good = Column(Boolean)
    variance = Column(Float)

    item = relationship("Item", back_populates="review_pairs")
    junior_review = relationship(
        "Review", foreign_keys=[junior_review_id])
    senior_review = relationship(
        "Review", foreign_keys=[senior_review_id])
