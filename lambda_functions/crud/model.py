from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean
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

    reviews = relationship("Review", backref="item")

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

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String)
    score = Column(Integer)
    level = Column(Integer)
    experience_points = Column(Integer)

    reviews = relationship("Review", backref="user")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "score": self.score, "level": self.level,
                "experience_points": self.experience_points}

class ReviewQuestion(Base):
    __tablename__ = 'review_questions'
    id = Column(String, primary_key=True)
    content = Column(String)
    mandatory = Column(Boolean)

    review_answers = relationship("ReviewAnswer", backref="review_question")

    def to_dict(self):
        return {"id": self.id, "content": self.content, "mandatory": self.mandatory}

class ReviewAnswer(Base):
    __tablename__ = 'review_answers'
    id = Column(String, primary_key=True)
    review_id = Column(String, ForeignKey('reviews.id'))
    review_question_id = Column(String, ForeignKey('review_questions.id'))
    answer = Column(Integer)
    comment = Column(String)

    def to_dict(self):
        return {"id": self.id, "review_id": self.review_id, "review_question_id": self.review_question_id,
                "answer": self.answer, "comment": self.comment}

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(String, primary_key=True)
    is_peer_review = Column(Boolean)
    initial_review_id = Column(String)
    item_id = Column(String, ForeignKey('items.id'))
    user_id = Column(String, ForeignKey('users.id'))
    review_answers = relationship("ReviewAnswer", backref="review")

    def to_dict(self):
        return {"id": self.id, "is_peer_review": self.is_peer_review, "initial_review_id": self.initial_review_id,
                "item_id": self.item_id, "user_id": self.user_id}