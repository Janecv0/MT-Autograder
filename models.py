from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="Student")
    is_active = Column(Boolean, default=True)
    items = relationship("Item", back_populates="owner")
    assignments = relationship("Assignment", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    filename = Column(String, index=True, unique=True, default=None)
    description = Column(String, default=None)
    tested = Column(Boolean, default=False)
    passed = Column(Boolean, default=False)
    mark = Column(Integer, default=0)
    pass_point = Column(Integer, default=0)
    fail_point = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    assignment = relationship("Assignment", back_populates="items")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    filename = Column(String, index=True, default=None)
    description = Column(String, default=None)
    github_url = Column(String, default=None)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="assignments")
    items = relationship("Item", back_populates="assignment")
