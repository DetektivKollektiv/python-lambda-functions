from sqlalchemy import Table, Column, DateTime, String, Integer, ForeignKey, func, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .model_base import Base


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
