from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """
    Represents a user in the db.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password of the user.
        role (str): The role of the user (default is "Student").
        is_active (bool): Indicates if the user is active (default is True).
        items (relationship): The items owned by the user.
        assignments (relationship): The assignments owned by the user.
        classrooms (relationship): The classrooms owned by the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    roles = relationship(
        "Role", secondary="user_roles", back_populates="users", passive_deletes=True
    )  # many to many
    is_active = Column(Boolean, default=True)
    items = relationship("Item", back_populates="owner")
    own_assignments = relationship("Assignment", back_populates="owner")  # one to many
    own_classrooms = relationship("Classroom", back_populates="owner")  # one to many
    classrooms = relationship(
        "Classroom",
        secondary="user_classroom",
        back_populates="students",
        passive_deletes=True,
    )  # many to many


class Item(Base):
    """
    Represents an item (homework) in the db.

    Attributes:
        id (int): The unique identifier of the item.
        filename (str): The filename of the item.
        description (str): The description of the item.
        tested (bool): Indicates if the item has been tested (default is False).
        passed (bool): Indicates if the item has passed the test (default is False).
        mark (int): The mark of the item (default is 0).
        pass_point (int): The pass point of the item (default is 0).
        fail_point (int): The fail point of the item (default is 0).
        owner_id (int): The ID of the owner of the item.
        owner (relationship): The owner of the item.
        assignment_id (int): The ID of the assignment the item belongs to.
        assignment (relationship): The assignment the item belongs to.
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    filename = Column(String, index=True, unique=True, default=None)
    description = Column(String, default=None)
    tested = Column(Boolean, default=False)
    passed = Column(Boolean, default=False)
    mark = Column(Integer, default=0)
    pass_point = Column(Integer, default=0)
    fail_point = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="items")
    assignment_id = Column(
        Integer, ForeignKey("assignments.id"), default=None, index=True
    )
    assignment = relationship("Assignment", back_populates="items")


class Assignment(Base):
    """
    Represents an assignment in the db.

    Attributes:
        id (int): The unique identifier of the assignment.
        filename (str): The filename of the assignment.
        description (str): The description of the assignment.
        github_url (str): The GitHub URL of the assignment.
        owner_id (int): The ID of the owner of the assignment.
        owner (relationship): The owner of the assignment.
        items (relationship): The items belonging to the assignment.
    """

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    filename = Column(String, index=True, default=None)
    description = Column(String, default=None)
    github_url = Column(String, default=None)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="own_assignments")
    items = relationship("Item", back_populates="assignment")
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), index=True
    )
    classroom = relationship("Classroom", back_populates="assignments")


class Classroom(Base):
    """
    Represents a classroom in the db.

    Attributes:
        id (int): The unique identifier of the classroom.
        name (str): The name of the classroom.
        description (str): The description of the classroom.
        year (int): The year of the classroom.
        owner_id (int): The ID of the owner of the classroom.
        owner (relationship): The owner of the classroom.
        assignments (relationship): The assignments belonging to the classroom.
        list_of_students (list): The list of students in the classroom.
    """

    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, default=None)
    description = Column(String, default=None)
    year = Column(Integer, default=None)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="own_classrooms")
    assignments = relationship(
        "Assignment", back_populates="classroom", passive_deletes=True
    )
    students = relationship(
        "User", secondary="user_classroom", back_populates="classrooms"
    )


class UserClassroom(Base):
    """
    Represents the association between users and classrooms.

    Attributes:
        user_id (int): The ID of the user.
        classroom_id (int): The ID of the classroom.
    """

    __tablename__ = "user_classroom"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), primary_key=True
    )


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    slug = Column(String(80), nullable=False, unique=True)

    users = relationship(
        "User", secondary="user_roles", back_populates="roles", passive_deletes=True
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
