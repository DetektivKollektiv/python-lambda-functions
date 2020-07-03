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
    factchecks = relationship("ExternalFactCheck")
    entities = relationship("ItemEntity", back_populates="item")
    urls = relationship("ItemURL", back_populates="item")
    sentiments = relationship("ItemSentiment", back_populates="item")
    keyphrases = relationship("ItemKeyphrase", back_populates="item")

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

class ExternalFactCheck(Base):
    __tablename__ = 'factchecks'
    id = Column(String, primary_key=True)
    url = Column(String)
    factchecking_organization_id = Column(String, ForeignKey('factchecking_organizations.id'))
    factchecking_organization = relationship("FactChecking_Organization", back_populates="factchecks")
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="factchecks")

class FactChecking_Organization(Base):
    __tablename__ = 'factchecking_organizations'
    id = Column(String, primary_key=True)
    name = Column(String)
    counter_trustworthy = Column(Integer)
    counter_not_trustworthy = Column(Integer)
    factchecks = relationship("ExternalFactCheck")

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(String, primary_key=True)
    entity = Column(String)
    items = relationship("ItemEntity", back_populates="entity")

class ItemEntity(Base):
    __tablename__ = 'item_entities'
    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="entities")
    entity_id = Column(String, ForeignKey('entities.id'))
    entity = relationship("Entity", back_populates="items")

class URL(Base):
    __tablename__ = 'urls'
    id = Column(String, primary_key=True)
    url = Column(String)
    items = relationship("ItemURL", back_populates="url")

class ItemURL(Base):
    __tablename__ = 'item_urls'
    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="urls")
    url_id = Column(String, ForeignKey('urls.id'))
    url = relationship("URL", back_populates="items")

class Sentiment(Base):
    __tablename__ = 'sentiments'
    id = Column(String, primary_key=True)
    sentiment = Column(String)
    items = relationship("ItemSentiment", back_populates="sentiment")

class ItemSentiment(Base):
    __tablename__ = 'item_sentiments'
    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="sentiments")
    sentiment_id = Column(String, ForeignKey('sentiments.id'))
    sentiment = relationship("Sentiment", back_populates="items")

class Keyphrase(Base):
    __tablename__ = 'keyphrases'
    id = Column(String, primary_key=True)
    keyphrase = Column(String)
    items = relationship("ItemKeyphrase", back_populates="keyphrase")

class ItemKeyphrase(Base):
    __tablename__ = 'item_keyphrases'
    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="keyphrases")
    keyphrase_id = Column(String, ForeignKey('keyphrases.id'))
    keyphrase = relationship("Keyphrase", back_populates="items")