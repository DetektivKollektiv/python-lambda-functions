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
    entities = relationship("Entity")


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

class ItemEntity(Base):
    __tablename__ = 'item_entities'
    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="item_entities")
    entity_id = Column(String, ForeignKey('entities.id'))
    entity = relationship("Entity", back_populates="item_entities")


class Entity(Base):
    __tablename__ = 'entities'
    id = Column(String, primary_key=True)
    entity = Column(String)
    item_entities = relationship("ItemEntity")


class ItemURL(Base):
    __tablename__ = 'item_urls'
    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="item_urls")
    url_id = Column(String, ForeignKey('urls.id'))
    url = relationship("Sentiment", back_populates="item_urls")


class URL(Base):
    __tablename__ = 'urls'
    id = Column(String, primary_key=True)
    url = Column(String)
    item_urls = relationship("ItemURL")


class ItemSentiment(Base):
    __tablename__ = 'item_sentiment'
    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('items.id'))
    item = relationship("Item", back_populates="item_sentiment")
    sentiment_id = Column(String, ForeignKey('sentiments.id'))
    sentiment = relationship("Sentiment", back_populates="item_sentiment")


class Sentiment(Base):
    __tablename__ = 'sentiments'
    id = Column(String, primary_key=True)
    sentiment = Column(String)
    item_sentiment = relationship("ItemSentiment")
