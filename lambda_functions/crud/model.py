from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'
    id = Column(String, primary_key=True)
    content = Column(String)
    language = Column(String)
    status = Column(String)
    variance = Column(Float)
    result_score = Column(Float)
    submissions = relationship("Submission")

    def to_dict(self):
        return {"id": self.id, "content": self.content, "language": self.language, "status": self.status,
                "variance": self.variance, "result_score": self.result_score}



class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(String, primary_key=True)
    submission_date = Column(DateTime)
    mail = Column(String)
    phone = Column(String)
    source = Column(String)
    frequency = Column(String)
    received_date = Column(DateTime)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="submissions")

    def to_dict(self):
        return {"id": self.id, "submission_date": self.submission_date, "mail": self.mail, "phone": self.phone,
                "source": self.source, "frequency": self.frequency, "received_date": self.received_date,
                "item_id": self.item_id}