from sqlalchemy import Column, DateTime, String
from .model_base import Base
from sqlalchemy.sql import func

"""
Store confirmation status of mail addresses.
"""

class Mail(Base):
    __tablename__ = 'mails'
    id = Column(String(36), primary_key = True)
    timestamp = Column(DateTime, server_default = func.now())
    email = Column(String)
    status = Column(String(100), default = "unconfirmed") # e.g. unconfirmed, confirmed, unsubscribed