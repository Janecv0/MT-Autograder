from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Item, Assignment, Classroom, Role, Base
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
    {"name": "Super teacher", "slug": "super_teacher"},
    {"name": "Teacher", "slug": "teacher"},
    {"name": "Student", "slug": "student"},
]

roles = []
for role_data in roles_data:
    role = Role(**role_data)
    roles.append(role)
    session.add(role)

# Commit the roles to the database
session.commit()

# Create users
users_data = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "role_id": roles[0].id,
    },
    {
        "username": "teacher",
        "email": "teacher@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "role_id": roles[1].id,
    },
    {
        "username": "student1",
        "email": "student1@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "role_id": roles[3].id,
    },
    {
        "username": "student2",
        "email": "student2@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "role_id": roles[3].id,
    },
    {
        "username": "student3",
        "email": "student3@example.com",
        "hashed_password": f"{get_password_hash('1234')}",
        "role_id": roles[3].id,
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
    filename="test_HW_1",
    description="First Assignment",
    owner=teacher,
    classroom=classroom,
    name="Assignment1",
)
assignment2 = Assignment(
    name="Assignment2",
    description="Second Assignment",
    owner=teacher,
    classroom=classroom,
    filename="test_HW_2",
)
session.add(assignment1)
session.add(assignment2)

# Add students to the classroom
students = users[2:]  # Exclude admin and teacher
for student in students:
    classroom.students.append(student)

# Commit the session to the database
session.commit()

# Close the session
session.close()
