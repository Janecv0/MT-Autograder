from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password of the user.
        role_id (int): The foreign key referencing the user's role.
        role (Role): The role of the user.
        is_active (bool): Indicates whether the user is active or not.
        items (List[Item]): The items owned by the user.
        own_assignments (List[Assignment]): The assignments owned by the user.
        own_classrooms (List[Classroom]): The classrooms owned by the user.
        classrooms (List[Classroom]): The classrooms the user is enrolled in.
        is_first_login (bool): Indicates whether it is the user's first login or not.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))  # one to many
    role = relationship("Role", back_populates="users")
    is_active = Column(Boolean, default=True)
    items = relationship("Item", back_populates="owner")
    own_assignments = relationship("Assignment", back_populates="owner")  # one to many
    own_classrooms = relationship("Classroom", back_populates="owner")  # one to many
    classrooms = relationship(
        "Classroom",
        secondary="user_classroom",
        back_populates="students",
        passive_deletes=True,
        cascade="all,delete",
    )  # many to many
    is_first_login = Column(Boolean, default=True)


class Item(Base):
    """
    Represents an item in the system.

    Attributes:
        id (int): The unique identifier of the item.
        filename (str): The filename of the item.
        description (str): The description of the item.
        tested (bool): Indicates whether the item has been tested.
        passed (bool): Indicates whether the item has passed the test.
        mark (int): The mark assigned to the item.
        pass_point (int): The pass point for the item.
        fail_point (int): The fail point for the item.
        owner_id (int): The ID of the owner of the item.
        owner (User): The owner of the item.
        assignment_id (int): The ID of the assignment the item belongs to.
        assignment (Assignment): The assignment the item belongs to.
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
    Represents an assignment in the system.

    Attributes:
        id (int): The unique identifier for the assignment.
        name (str): The name of the assignment.
        filename (str): The filename associated with the assignment.
        description (str): The description of the assignment.
        github_url (str): The GitHub URL for the assignment.
        owner_id (int): The ID of the owner of the assignment.
        owner (User): The owner of the assignment.
        items (List[Item]): The items associated with the assignment.
        classroom_id (int): The ID of the classroom the assignment belongs to.
        classroom (Classroom): The classroom the assignment belongs to.
    """

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, default=None)
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
    Represents a classroom in the system.

    Attributes:
        id (int): The unique identifier of the classroom.
        name (str): The name of the classroom.
        description (str): The description of the classroom.
        year (int): The year of the classroom.
        owner_id (int): The ID of the owner of the classroom.
        owner (User): The owner of the classroom.
        assignments (List[Assignment]): The assignments associated with the classroom.
        students (List[User]): The students enrolled in the classroom.
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
        "User",
        secondary="user_classroom",
        back_populates="classrooms",
        cascade="all,delete",
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
    """
    Represents a role in the system.

    Attributes:
        id (int): The unique identifier for the role.
        name (str): The name of the role.
        slug (str): The slug of the role.
        users (list): The list of users associated with the role.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    slug = Column(String(80), nullable=False, unique=True)

    users = relationship(
        "User", back_populates="role", passive_deletes=True
    )  # one to many
