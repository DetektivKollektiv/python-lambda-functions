from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .model_base import Base
from uuid import uuid4


def generate_uuid():
    return str(uuid4())


class Issue(Base):
    __tablename__ = 'issues'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    category = Column(String(100), nullable=False)
    message = Column(String(1000), nullable=False)
    ip_address = Column(String(15))

    # Entity to which the issue refers to (only one of them may be filled)
    item_id = Column(String(36), ForeignKey('items.id',
                                            ondelete='SET NULL', onupdate='CASCADE'))
    item = relationship('Item')
    comment_id = Column(String(36), ForeignKey("comments.id"))
    comment = relationship("Comment", back_populates = "issues")

    def to_dict(self):
        return {
            'category': self.category,
            'message': self.message,
            'item_id': self.item_id
        }
