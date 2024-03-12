from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Item, Assignment, Classroom, Role, UserRole, Base
from crud import get_password_hash

# Create an engine to connect to the database
engine = create_engine("sqlite:///api.db")

# Create all tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create roles
roles_data = [
    {"name": "Admin", "slug": "admin"},
    {"name": "Teacher", "slug": "teacher"},
    {"name": "Student", "slug": "student"},
]

roles = []
for role_data in roles_data:
    role = Role(**role_data)
    roles.append(role)
    session.add(role)

# Create users
users_data = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "roles": [roles[0]],
    },
    {
        "username": "teacher",
        "email": "teacher@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "roles": [roles[1]],
    },
    {
        "username": "student1",
        "email": "student1@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "roles": [roles[2]],
    },
    {
        "username": "student2",
        "email": "student2@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "roles": [roles[2]],
    },
    {
        "username": "student3",
        "email": "student3@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "roles": [roles[2]],
    },
]

users = []
for user_data in users_data:
    user = User(**user_data)
    users.append(user)
    session.add(user)

# Create teacher's classroom
teacher = users[1]
classroom = Classroom(
    name="Math Class", description="Mathematics Classroom", year=2024, owner=teacher
)
session.add(classroom)

# Create assignments for the classroom
assignment1 = Assignment(
    filename="Assignment1",
    description="First Assignment",
    owner=teacher,
    classroom=classroom,
)
assignment2 = Assignment(
    filename="Assignment2",
    description="Second Assignment",
    owner=teacher,
    classroom=classroom,
)
session.add(assignment1)
session.add(assignment2)

# Add students to the classroom
students = users[2:]
for student in students:
    classroom.students.append(student)

# Create items for each student corresponding to the first assignment
for student in students:
    item = Item(
        filename=f"{student.username}_assignment1",
        description=f"Item for {student.username}",
        owner=student,
        assignment=assignment1,
    )
    session.add(item)

# Commit the session to the database
session.commit()

# Close the session
session.close()
