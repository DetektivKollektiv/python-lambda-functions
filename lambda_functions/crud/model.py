from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'
    id = Column(String(36), primary_key=True)
    type = Column(String(36))
    content = Column(Text)
    language = Column(String(2))
    status = Column(String(36))
    variance = Column(Float)
    result_score = Column(Float)
    open_reviews = Column(Integer)
    open_reviews_level_1 = Column(Integer)
    open_reviews_level_2 = Column(Integer)
    in_progress_reviews_level_1 = Column(Integer)
    in_progress_reviews_level_2 = Column(Integer)
    open_timestamp = Column(DateTime)
    close_timestamp = Column(DateTime)

    submissions = relationship("Submission")
    factchecks = relationship("ExternalFactCheck")
    entities = relationship("ItemEntity")
    urls = relationship("ItemURL")
    sentiments = relationship("ItemSentiment")
    keyphrases = relationship("ItemKeyphrase")

    reviews = relationship("Review", backref="item")

    def to_dict(self):
        return {"id": self.id, "content": self.content, "language": self.language, "status": self.status,
                "variance": self.variance, "result_score": self.result_score,
                "open_reviews_level_1": self.open_reviews_level_1, "open_reviews_level_2": self.open_reviews_level_2, "open_reviews": self.open_reviews,
                "open_timestamp": self.open_timestamp, "close_timestamp": self.close_timestamp, "in_progress_reviews_level_1": self.in_progress_reviews_level_1,
                "in_progress_reviews_level_2": self.in_progress_reviews_level_2}


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(String(36), primary_key=True)
    submission_date = Column(DateTime)
    mail = Column(String(100))
    telegram_id = Column(String(100))
    phone = Column(String(36))
    source = Column(String(100))
    frequency = Column(String(100))
    received_date = Column(DateTime)
    item_id = Column(String(36), ForeignKey('items.id'))
    item = relationship("Item", back_populates="submissions")

    def to_dict(self):
        return {"id": self.id, "submission_date": self.submission_date, "mail": self.mail, "telegram_id": self.telegram_id, "phone": self.phone,
                "source": self.source, "frequency": self.frequency, "received_date": self.received_date,
                "item_id": self.item_id}


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


class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    score = Column(Integer)
    experience_points = Column(Integer)
    level_id = Column(Integer, ForeignKey('levels.id'))

    level = relationship("Level", back_populates="users")
    reviews = relationship("Review", backref="user")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "score": self.score, "level": self.level_id, "level_description": self.level.description,
                "experience_points": self.experience_points}


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


class ReviewQuestion(Base):
    __tablename__ = 'review_questions'
    id = Column(String(36), primary_key=True)
    content = Column(Text)
    mandatory = Column(Boolean)
    info = Column(Text)

    review_answers = relationship("ReviewAnswer", backref="review_question")
    options = relationship("AnswerOption",
                           secondary=question_option_pairs,
                           back_populates="questions")

    def to_dict(self):
        return {"id": self.id, "content": self.content, "mandatory": self.mandatory, "info": self.info}

    def to_dict_with_answers(self):
        question = {"id": self.id, "content": self.content,
                    "mandatory": self.mandatory, "info": self.info, "options": []}
        for option in self.options:
            question["options"].append(option.to_dict())
        return question


class AnswerOption(Base):
    __tablename__ = 'answer_options'
    id = Column(String(36), primary_key=True)
    text = Column(Text)
    value = Column(Integer)
    questions = relationship(
        "ReviewQuestion", secondary=question_option_pairs, back_populates="options")

    def to_dict(self):
        return {"id": self.id, "text": self.text}


class ReviewAnswer(Base):
    __tablename__ = 'review_answers'
    id = Column(String(36), primary_key=True)
    review_id = Column(String(36), ForeignKey('reviews.id'))
    review_question_id = Column(String(36), ForeignKey(
        'review_questions.id', ondelete='CASCADE', onupdate='CASCADE'))
    answer = Column(Integer)
    comment = Column(Text)

    def to_dict(self):
        return {"id": self.id, "review_id": self.review_id, "review_question_id": self.review_question_id,
                "answer": self.answer, "comment": self.comment}


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(String(36), primary_key=True)
    is_peer_review = Column(Boolean)
    peer_review_id = Column(String(36))
    belongs_to_good_pair = Column(Boolean)
    item_id = Column(String(36), ForeignKey('items.id'))
    user_id = Column(String(36), ForeignKey('users.id'))
    review_answers = relationship("ReviewAnswer", backref="review")
    start_timestamp = Column(DateTime)
    finish_timestamp = Column(DateTime)
    status = Column(String(100))

    def to_dict(self):
        return {"id": self.id, "is_peer_review": self.is_peer_review, "peer_review_id": self.peer_review_id,
                "belongs_to_good_pair": self.belongs_to_good_pair, "item_id": self.item_id, "user_id": self.user_id,
                "start_timestamp": self.start_timestamp, "finish_timestamp": self.finish_timestamp}
