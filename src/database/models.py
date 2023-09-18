import enum

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, func, Boolean, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.types import ARRAY

Base = declarative_base()


class Model(enum.Enum):
    """
    Model the user uses.
    """
    falcon: str = 'falcon'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(), unique=True, nullable=False)
    is_bot = Column(Boolean, default=False, nullable=True)
    first_name = Column(String(), unique=False, nullable=False)
    username = Column(String(), unique=False, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now())
    model = Column('models', Enum(Model), default=Model.falcon)
    use_docs = ARRAY(Integer, as_tuple=False, dimensions=None, zero_indexes=False)
    docs = relationship("Doc", back_populates="user")


class Doc(Base):
    __tablename__ = 'docs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="docs")
    name = Column(String(), unique=False, nullable=False)
    description = Column(String(), unique=False, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)
