from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ExternalFactCheck(Base):
    __tablename__ = 'factchecks'
    id = Column(String(36), primary_key=True)
    title = Column(String(1000))
    url = Column(String(1000))
    factchecking_organization_id = Column(
        String(36), ForeignKey('factchecking_organizations.id'))
    factchecking_organization = relationship(
        "FactChecking_Organization", back_populates="factchecks")
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="factchecks")

    def to_dict(self):
        return {"id": self.id, "url": self.url, "title": self.title}


class FactChecking_Organization(Base):
    __tablename__ = 'factchecking_organizations'
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    counter_trustworthy = Column(Integer)
    counter_not_trustworthy = Column(Integer)
    factchecks = relationship("ExternalFactCheck")


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


class Claimant(Base):
    __tablename__ = 'claimants'
    id = Column(String(36), primary_key=True)
    claimant = Column(String(200))
    url = relationship("URL")


class URL(Base):
    __tablename__ = 'urls'
    id = Column(String(36), primary_key=True)
    url = Column(String(200))
    items = relationship("ItemURL")
    claimant_id = Column(String(36), ForeignKey('claimants.id'))
    claimant = relationship("Claimant", back_populates="url")


class ItemURL(Base):
    __tablename__ = 'item_urls'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="urls")
    url_id = Column(String(36), ForeignKey('urls.id'))
    url = relationship("URL", back_populates="items")


class Sentiment(Base):
    __tablename__ = 'sentiments'
    id = Column(String(36), primary_key=True)
    sentiment = Column(String(200))
    items = relationship("ItemSentiment")


class ItemSentiment(Base):
    __tablename__ = 'item_sentiments'
    id = Column(String(36), primary_key=True)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="sentiments")
    sentiment_id = Column(String(36), ForeignKey('sentiments.id'))
    sentiment = relationship("Sentiment", back_populates="items")


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


class Level(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    required_experience_points = Column(Integer)

    users = relationship("User", back_populates="level")


question_option_pairs = Table('question_option_pairs', Base.metadata,
                              Column('question_id', String(36),
                                     ForeignKey('review_questions.id')),
                              Column('option_id', String(36),
                                     ForeignKey('answer_options.id'))
                              )


class AnswerOption(Base):
    __tablename__ = 'answer_options'
    id = Column(String(36), primary_key=True)
    text = Column(Text)
    value = Column(Integer)
    questions = relationship(
        "ReviewQuestion", secondary=question_option_pairs, back_populates="options")

    def to_dict(self):
        return {"id": self.id, "text": self.text, "value": self.value}
