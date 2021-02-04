from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


class Item(Base):
    __tablename__ = 'items'
    id = Column(String(36), primary_key=True)
    type = Column(String(36))
    content = Column(Text)
    language = Column(String(2))
    status = Column(String(36), default='unconfirmed')
    variance = Column(Float)
    result_score = Column(Float)
    open_reviews = Column(Integer)
    open_reviews_level_1 = Column(Integer)
    open_reviews_level_2 = Column(Integer)
    in_progress_reviews_level_1 = Column(Integer)
    in_progress_reviews_level_2 = Column(Integer)
    open_timestamp = Column(DateTime)
    close_timestamp = Column(DateTime)
    verification_process_version = Column(Integer)

    item_type_id = Column(String(36), ForeignKey(
        'item_types.id', ondelete='SET NULL', onupdate='CASCADE'))

    submissions = relationship("Submission")
    factchecks = relationship("ExternalFactCheck")
    entities = relationship("ItemEntity")
    tags = relationship("ItemTag")
    urls = relationship("ItemURL")
    sentiments = relationship("ItemSentiment")
    keyphrases = relationship("ItemKeyphrase")
    reviews = relationship("Review", back_populates="item")
    review_pairs = relationship("ReviewPair", back_populates="item")
    item_type = relationship("ItemType", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "item_type_id": self.item_type_id,
            "content": self.content,
            "language": self.language,
            "status": self.status,
            "variance": self.variance,
            "result_score": self.result_score,
            "open_reviews_level_1": self.open_reviews_level_1,
            "open_reviews_level_2": self.open_reviews_level_2,
            "open_reviews": self.open_reviews,
            "open_timestamp": self.open_timestamp,
            "close_timestamp": self.close_timestamp,
            "in_progress_reviews_level_1": self.in_progress_reviews_level_1,
            "in_progress_reviews_level_2": self.in_progress_reviews_level_2
        }
