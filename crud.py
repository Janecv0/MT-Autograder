from sqlalchemy.orm import Session

import models, schemas
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_role(db: Session, role: str):
    return db.query(models.User).filter(models.User.role == role).first()


def get_user_role(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first().role


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        username=user.username,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_item(db: Session, filename: str):
    return db.query(models.Item).filter(models.Item.filename == filename).first()


def get_item_by_id(db: Session, id: int) -> models.Item:
    return db.query(models.Item).filter(models.Item.id == id).first()


def get_user_item(db: Session, user_id: int):
    return db.query(models.Item).filter(models.Item.owner_id == user_id).first()


def create_user_item(
    db: Session,
    item: schemas.ItemCreate,
    user_id: int,
    filename: str,
    ass_id: int,
):
    db_item = models.Item(
        description=item.description,
    )
    db_item.filename = filename
    db_item.owner_id = user_id
    db_item.assignment_id = ass_id
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def is_teacher(db: Session, user_id: int):
    return (
        True
        if db.query(models.User).filter(models.User.id == user_id).first().role
        == "Teacher"
        else False
    )


def update_item(
    db: Session,
    item_id: int,
    tested: bool,
    passed: bool,
    mark: int,
    pass_point: int,
    fail_point: int,
):
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
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.email = user.email
    db_user.username = user.username
    db_user.role = user.role
    db_user.hashed_password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_item(db: Session, item_id: int):
    db.query(models.Item).filter(models.Item.id == item_id).delete()
    db.commit()
    return {"message": "Item deleted successfully"}


def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return {"message": "User deleted successfully"}


def create_assignment(
    db: Session, assignment: schemas.AssignmentCreate, user_id: int
):
    db_assignment = models.Assignment(
        description=assignment.description,
        github_url=assignment.github_url,
        filename=assignment.filename
    )
    db_assignment.filename = assignment.filename
    db_assignment.owner_id = user_id
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_assignments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Assignment).offset(skip).limit(limit).all()

def get_assignment_by_id(db: Session, assignment_id: int):
    return db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

def get_my_assignments(db: Session, user_id: int):
    return db.query(models.Assignment).filter(models.Assignment.owner_id == user_id).all()

def update_assignment(
    db: Session,
    assignment_id: int,
    description: str,
    github_url: str,
    filename: str,
):
    db_assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    db_assignment.description = description
    db_assignment.github_url = github_url
    db_assignment.filename = filename
    db.commit()
    db.refresh(db_assignment)
    return db_assignment
