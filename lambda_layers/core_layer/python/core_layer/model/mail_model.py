from sqlalchemy import Column, DateTime, String, ForeignKey
from .model_base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref

"""
Store mail addresses and subscription status.
"""

class Mail(Base):
    __tablename__ = 'mails'
    id = Column(String(36), primary_key = True)
    timestamp = Column(DateTime, server_default = func.now())
    email = Column(String(100), unique = True)
    status = Column(String(100), default = 'unconfirmed') # e.g. unconfirmed, confirmed, unsubscribed

    # Relationships
    # one-to-many
    submissions = relationship('Submission', back_populates = "mail") # adds a 'virtual column' with a list of all submissions belonging to this mail address
    users = relationship('User', back_populates = "mail")