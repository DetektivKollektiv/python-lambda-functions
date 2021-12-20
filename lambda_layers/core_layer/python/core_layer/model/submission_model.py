from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from .model_base import Base


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(String(36), primary_key=True)
    submission_date = Column(DateTime)
    telegram_id = Column(String(100))
    phone = Column(String(36))
    source = Column(String(100))
    channel = Column(String(100))
    frequency = Column(String(100))
    received_date = Column(DateTime)
    ip_address = Column(String(15))
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="submissions")
    comments = relationship("Comment", back_populates="submission")

    def to_dict(self):
        return {
            "id": self.id,
            "submission_date": self.submission_date,
            "telegram_id": self.telegram_id,
            "phone": self.phone,
            "source": self.source,
            "frequency": self.frequency,
            "received_date": self.received_date,
            "item_id": self.item_id
        }