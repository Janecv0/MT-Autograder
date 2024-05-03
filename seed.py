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
        "username": "ucitel",
        "email": "nejucitel@email.cz",
        "hashed_password": f"{get_password_hash('1234')}",
        "role_id": roles[1].id,
    },
    {
        "username": "janecvoj",
        "email": "vojtech.janecek@fs.cvut.cz",
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

classrooms =[ Classroom(
    name="S232-OOP", description="Objektově orientované programování", year=2024, owner=teacher
),
    Classroom(
        name="S232-AI", description="Umělá inteligence a neuronové sítě", year=2024, owner=teacher
    ),
    Classroom(
        name="S232-SVAO", description="Strojové vnímání a analýza obrazu", year=2024, owner=teacher
    ),
    Classroom(
        name="S232-PIS", description="Projektování informačních systémů", year=2024, owner=teacher
    ),
    
    Classroom(
        name="S232-OPSR", description="Optimální a prediktivní systémy řízení", year=2024, owner=teacher
    ),
]
for classroom in classrooms:
    session.add(classroom)

# Create assignments for the classroom
assignment1 = Assignment(
    filename="test_HW_1",
    description="print('Hello World!')",
    owner=teacher,
    classroom=classrooms[0],
    name="Hello World!",
)
assignment2 = Assignment(
    name="FizzBuzz",
    description="FizzBuzz implementace v Pythonu.",
    owner=teacher,
    classroom=classrooms[0],
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
