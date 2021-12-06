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
    email = Column(String(100))
    status = Column(String(100), default = 'unconfirmed') # e.g. unconfirmed, confirmed, unsubscribed

    # Relationships
    # one-to-one
    user_id = Column(String(36), ForeignKey('users.id')) # adds a ForeignKey with the id of the user
    user = relationship('User', backref = backref('email', uselist = False)) # adds a virtual column 'user' with a link to the User table here - and creates a virtual column 'email' in User table