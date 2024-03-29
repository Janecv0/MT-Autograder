from sqlalchemy.orm import Session

import models, schemas
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    """
    Return the user with the given user_id

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        User: The user with the specified ID, or None if not found.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """
    Return the user with the given username

    Args:
        db (Session): The database session.
        username (str): The username of the user.

    Returns:
        User: The user with the specified username, or None if not found.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> models.User:
    """
    Return the user with the given email

    Args:
        db (Session): The database session.
        email (str): The email of the user.

    Returns:
        User: The user with the specified email, or None if not found.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Return a list of users with a given offset and limit

    Args:
        db (Session): The database session.
        skip (int, optional): Number of users to skip. Defaults to 0.
        limit (int, optional): Maximum number of users to retrieve. Defaults to 100.

    Returns:
        List[User]: List of users retrieved from the database.
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_role(db: Session, role: str):
    """
    Return the user with the given role

    Args:
        db (Session): The database session.
        role (str): The role of the user.

    Returns:
        User: The user with the specified role, or None if not found.
    """
    return (
        db.query(models.User)
        .join(models.User.roles)
        .filter(models.Role.name == role)
        .all()
    )


def get_user_role(db: Session, user_id: str):
    """
    Return the role of the user with the given user_id

    Args:
        db (Session): The database session.
        user_id (str): The ID of the user.

    Returns:
        str: The role of the user.
    """
    return (
        db.query(models.Role)
        .join(models.User.roles)
        .filter(models.User.id == user_id)
        .first()
        .name
    )


def get_password_hash(password):
    """
    Return the hashed password

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user with the given user details

    Args:
        db (Session): The database session.
        user (UserCreate): The user data to be created.

    Returns:
        User: The created user.
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        username=user.username,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def change_user_role(db: Session, user_id: int, role: str):
    """
    Change the role of a user with the given user_id

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        role (str): The new role of the user.

    Returns:
        User: The user with the updated role.
    """

    db_role = db.query(models.Role).filter(models.Role.name == role).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.roles.append(db_role)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all items from the database.

    Args:
        db (Session): The database session.
        skip (int, optional): Number of items to skip. Defaults to 0.
        limit (int, optional): Maximum number of items to retrieve. Defaults to 100.

    Returns:
        List[Item]: List of items retrieved from the database.
    """
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_item(db: Session, filename: str):
    """
    Retrieve an item from the database based on the filename.

    Args:
        db (Session): The database session.
        filename (str): The filename of the item to retrieve.

    Returns:
        Optional[models.Item]: The retrieved item, or None if not found.
    """
    return db.query(models.Item).filter(models.Item.filename == filename).first()


def get_item_by_id(db: Session, id: int) -> models.Item:
    """
    Retrieve an item from the database by its ID.

    Args:
        db (Session): The database session.
        id (int): The ID of the item to retrieve.

    Returns:
        models.Item: The item with the specified ID, or None if not found.
    """
    return db.query(models.Item).filter(models.Item.id == id).first()


def get_user_item(db: Session, user_id: int):
    """
    Retrieve an item owned by a specific user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        Item: The item owned by the user, or None if not found.
    """
    return db.query(models.Item).filter(models.Item.owner_id == user_id).first()


def create_user_item(
    db: Session,
    item: schemas.ItemCreate,
    user_id: int,
    ass_id: int,
):
    """
    Create a new item for a user in the database.

    Args:
        db (Session): The database session.
        item (ItemCreate): The item data to be created.
        user_id (int): The ID of the user.
        filename (str): The filename of the item.
        ass_id (int): The ID of the assignment.

    Returns:
        Item: The created item.
    """
    db_item = models.Item(
        description=item.description,
    )
    db_item.filename = f"HW_{ass_id}_{user_id}"
    db_item.owner_id = user_id
    db_item.assignment_id = ass_id
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def is_teacher(db: Session, user_id: int):
    """
    Check if a user is a teacher based on their role.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        bool: True if the user is a teacher, False otherwise.
    """

    if (
        db.query(models.User)
        .join(models.User.roles)
        .filter(models.User.id == user_id)
        .filter(models.Role.slug == "Teacher")
        is not None
    ):
        return True
    else:
        return False


def is_admin(db: Session, user_id: int):
    """
    Check if a user is a teacher based on their role.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        bool: True if the user is a teacher, False otherwise.
    """

    if (
        db.query(models.User)
        .join(models.User.roles)
        .filter(models.User.id == user_id)
        .filter(models.Role.slug == "Admin")
        is not None
    ):
        return True
    else:
        return False


def is_super_teacher(db: Session, user_id: int):
    """
    Check if a user is a teacher based on their role.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        bool: True if the user is a teacher, False otherwise.
    """

    if (
        db.query(models.User)
        .join(models.User.roles)
        .filter(models.User.id == user_id)
        .filter(models.Role.slug == "Super Teacher")
        is not None
    ):
        return True
    else:
        return False


def update_item(
    db: Session,
    item_id: int,
    tested: bool,
    passed: bool,
    mark: int,
    pass_point: int,
    fail_point: int,
):
    """
    Update an item in the database with the provided information.

    Args:
        db (Session): The database session.
        item_id (int): The ID of the item to be updated.
        tested (bool): Whether the item has been tested.
        passed (bool): Whether the item has passed the test.
        mark (int): The mark assigned to the item.
        pass_point (int): The passing point for the item.
        fail_point (int): The failing point for the item.

    Returns:
        Item: The updated item.
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    db_item.tested = tested
    db_item.passed = passed
    db_item.mark = mark
    db_item.pass_point = pass_point
    db_item.fail_point = fail_point

    db.commit()
    db.refresh(db_item)
    return db_item


def update_user(db: Session, user_id: int, user: schemas.User):
    """
    Update a user in the database with the provided information.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to be updated.
        user (User): The updated user data.

    Returns:
        User: The updated user.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.email = user.email
    db_user.username = user.username
    db_user.role = user.role
    db_user.hashed_password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_password(db: Session, user_id: int, password: str):
    """
    Update the password of a user in the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to be updated.
        password (str): The new password.

    Returns:
        User: The updated user.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_item(db: Session, item_id: int):
    """
    Delete an item from the database.

    Args:
        db (Session): The database session.
        item_id (int): The ID of the item to be deleted.

    Returns:
        dict: A dictionary with a message indicating the success of the deletion.
    """
    db.query(models.Item).filter(models.Item.id == item_id).delete()
    db.commit()
    return {"message": "Item deleted successfully"}


def delete_user(db: Session, user_id: int):
    """
    Delete a user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to be deleted.

    Returns:
        dict: A dictionary with a message indicating the success of the deletion.
    """
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return {"message": "User deleted successfully"}


def create_assignment(db: Session, assignment: schemas.AssignmentCreate, user_id: int):
    """
    Create a new assignment in the database.

    Args:
        db (Session): The database session.
        assignment (AssignmentCreate): The assignment data to be created.
        user_id (int): The ID of the user.

    Returns:
        Assignment: The created assignment.
    """
    db_assignment = models.Assignment(
        description=assignment.description,
        github_url=assignment.github_url,
        filename=assignment.filename,
    )
    db_assignment.filename = assignment.filename
    db_assignment.owner_id = user_id
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def get_assignments(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all assignments from the database.

    Args:
        db (Session): The database session.
        skip (int, optional): Number of assignments to skip. Defaults to 0.
        limit (int, optional): Maximum number of assignments to retrieve. Defaults to 100.

    Returns:
        List[Assignment]: List of assignments retrieved from the database.
    """
    return db.query(models.Assignment).offset(skip).limit(limit).all()


def get_assignment_by_id(db: Session, assignment_id: int):
    """
    Retrieve an assignment from the database by its ID.

    Args:
        db (Session): The database session.
        assignment_id (int): The ID of the assignment to retrieve.

    Returns:
        Assignment: The assignment with the specified ID, or None if not found.
    """
    return (
        db.query(models.Assignment)
        .filter(models.Assignment.id == assignment_id)
        .first()
    )


def get_my_assignments(db: Session, user_id: int):
    """
    Retrieve assignments owned by a specific user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[Assignment]: List of assignments owned by the user.
    """
    return (
        db.query(models.Assignment).filter(models.Assignment.owner_id == user_id).all()
    )


def update_assignment(
    db: Session,
    assignment_id: int,
    description: str,
    github_url: str,
    filename: str,
):
    """
    Update an assignment in the database with the provided information.

    Args:
        db (Session): The database session.
        assignment_id (int): The ID of the assignment to be updated.
        description (str): The updated description of the assignment.
        github_url (str): The updated GitHub URL of the assignment.
        filename (str): The updated filename of the assignment.

    Returns:
        Assignment: The updated assignment.
    """
    db_assignment = (
        db.query(models.Assignment)
        .filter(models.Assignment.id == assignment_id)
        .first()
    )
    db_assignment.description = description
    db_assignment.github_url = github_url
    db_assignment.filename = filename
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def create_classroom(db: Session, classroom: schemas.ClassroomCreate, user_id: int):
    """
    Create a new classroom in the database.

    Args:
        db (Session): The database session.
        classroom (ClassroomCreate): The classroom data to be created.
        user_id (int): The ID of the user.

    Returns:
        Classroom: The created classroom.
    """
    db_classroom = models.Classroom(
        name=classroom.name,
        description=classroom.description,
        year=classroom.year,
    )
    db_classroom.owner_id = user_id
    db.add(db_classroom)
    db.commit()
    db.refresh(db_classroom)
    return db_classroom


def get_classrooms(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all classrooms from the database.

    Args:
        db (Session): The database session.
        skip (int, optional): Number of classrooms to skip. Defaults to 0.
        limit (int, optional): Maximum number of classrooms to retrieve. Defaults to 100.

    Returns:
        List[Classroom]: List of classrooms retrieved from the database.
    """
    return db.query(models.Classroom).offset(skip).limit(limit).all()


def get_classroom_by_id(db: Session, classroom_id: int):
    """
    Retrieve a classroom from the database by its ID.

    Args:
        db (Session): The database session.
        classroom_id (int): The ID of the classroom to retrieve.

    Returns:
        Classroom: The classroom with the specified ID, or None if not found.
    """
    return (
        db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    )


def is_student_in_db(db: Session, student_id: int):
    """
    Check if a student is in the database.

    Args:
        db (Session): The database session.
        student_id (int): The ID of the student.

    Returns:
        bool: True if the student is in the database, False otherwise.
    """
    return (
        True
        if db.query(models.User).filter(models.User.id == student_id).first().role
        == "Student"
        else False
    )


def is_user_in_db(db: Session, email: str):
    """
    Check if a student is in the database based on email.

    Args:
        db (Session): The database session.
        student_id (int): The ID of the student.

    Returns:
        bool: True if the student is in the database, False otherwise.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is not None:
        return True
    return False


def is_student_in_classroom(db: Session, classroom_id: int, student_id: int):
    """
    Check if a student is in a classroom.

    Args:
        db (Session): The database session.
        classroom_id (int): The ID of the classroom.
        student_id (int): The ID of the student.

    Returns:
        bool: True if the student is in the classroom, False otherwise.
    """
    db_classroom = db.query(models.Classroom).join(models.Classroom.students).all()
    for student in db_classroom:
        if student.id == student_id:
            return True
    else:
        return False


def enroll_student(db: Session, classroom_id: int, user_id: int):
    """
    Add a student to a classroom in the database.

    Args:
        db (Session): The database session.
        classroom_id (int): The ID of the classroom.
        student_id (int): The ID of the student.

    Returns:
        Classroom: The updated classroom.
    """
    db_classroom = (
        db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    )
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_classroom.students.append(db_user)
    db.commit()
    db.refresh(db_classroom)
    return db_classroom


def get_my_classrooms(db: Session, user_id: int):
    """
    Return classes in which is user enrolled.
    """
    return (
        db.query(models.Classroom)
        .join(models.Classroom.students)
        .filter(models.User.id == user_id)
        .all()
    )
