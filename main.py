from datetime import datetime, timedelta, timezone
from typing import Annotated
from secrets import token_hex

from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

from run_tests import run_tests


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

"""Authentication"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


@app.get("/")
def read_root():
    """
    Root endpoint to check if the server is running.
    """
    return "Server is running!"


def get_db():
    """
    Dependency function to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    """
    Verify if the plain password matches the hashed password.

    Args:
        plain_password (str): The plain password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Generate the hash of a password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Authenticate a user based on the provided username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The authenticated user if successful, False otherwise.
    """
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create an access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta | None, optional): The expiration time of the token. Defaults to None.

    Returns:
        str: The encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    """
    Get the current authenticated user based on the provided token.

    Args:
        token (str): The access token.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: If the credentials cannot be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    """
    Get the current active user.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        User: The current active user.

    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> schemas.Token:
    """
    Login endpoint to obtain an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Token: The access token.

    Raises:
        HTTPException: If the username or password is incorrect.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
    """
    Get the current authenticated user.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        User: The current authenticated user.
    """
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Get the items owned by the current authenticated user.

    Args:
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[Item]: The items owned by the current authenticated user.
    """
    return crud.get_user_item(db, user_id=current_user.id)


"""Database operations"""


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user (UserCreate): The user data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The created user.

    Raises:
        HTTPException: If the email is already registered.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get a list of users.

    Args:
        current_user (User): The current authenticated user.
        skip (int, optional): The number of users to skip. Defaults to 0.
        limit (int, optional): The maximum number of users to return. Defaults to 100.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[User]: The list of users.

    Raises:
        HTTPException: If the current user is not a teacher.
    """
    if crud.is_teacher(db, current_user.id):
        users = crud.get_users(db, skip=skip, limit=limit)
        return users
    else:
        raise HTTPException(status_code=401, detail="You are not a teacher")


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user_id(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a user by ID.

    Args:
        current_user (User): The current authenticated user.
        user_id (int): The ID of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user with the specified ID.

    Raises:
        HTTPException: If the current user is not a teacher or the user is not found.
    """
    if crud.is_teacher(db, current_user.id):
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    else:
        raise HTTPException(status_code=401, detail="You are not a teacher")


@app.get("/users/by_username/{username}", response_model=schemas.User)
def read_user_username(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    username: str,
    db: Session = Depends(get_db),
):
    """
    Get a user by username.

    Args:
        current_user (User): The current authenticated user.
        username (str): The username of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user with the specified username.

    Raises:
        HTTPException: If the current user is not a teacher or the user is not found.
    """
    if crud.is_teacher(db, current_user.id):
        db_user = crud.get_user_by_username(db, username=username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    else:
        raise HTTPException(status_code=401, detail="You are not a teacher")


@app.get("/users/by_email/{email}", response_model=schemas.User)
def read_user_email(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    email: str,
    db: Session = Depends(get_db),
):
    """
    Get a user by email.

    Args:
        current_user (User): The current authenticated user.
        email (str): The email of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user with the specified email.

    Raises:
        HTTPException: If the current user is not a teacher or the user is not found.
    """
    if crud.is_teacher(db, current_user.id):
        db_user = crud.get_user_by_email(db, email=email)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    else:
        raise HTTPException(status_code=401, detail="You are not a teacher")


@app.get("/users/by_role/{role}", response_model=schemas.User)
def read_user_by_role(role: str, db: Session = Depends(get_db)):
    """
    Get a user by role.

    Args:
        role (str): The role of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user with the specified role.

    Raises:
        HTTPException: If the user is not found.
    """
    db_user = crud.get_user_by_role(db, role=role)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/role/")
def read_user_role(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Get the role of the current authenticated user.

    Args:
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        str: The role of the current authenticated user.
    """
    return crud.get_user_role(db, current_user.id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of items.

    Args:
        skip (int, optional): The number of items to skip. Defaults to 0.
        limit (int, optional): The maximum number of items to return. Defaults to 100.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[Item]: The list of items.
    """
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.put("/users/me/update/", response_model=schemas.User)
def update_user(
    user: schemas.UserCreate,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Update the current authenticated user.

    Args:
        user (UserCreate): The updated user data.
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The updated user.
    """
    user_id = current_user.id
    return crud.update_user(db=db, user=user, user_id=user_id)


def create_item(
    ass_id: int,
    item: schemas.ItemCreate,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Create an item.

    Args:
        ass_id (int): The ID of the assignment.
        item (ItemCreate): The item data.
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Item: The created item.

    Raises:
        HTTPException: If a file with the same name already exists.
    """
    # if file with same name already exists
    filename = f"HW_1_{current_user.username}"
    db_item = crud.get_item(db=db, filename=filename)
    if db_item:
        raise HTTPException(status_code=400, detail="File already updated")
    else:
        return crud.create_user_item(
            db=db,
            item=item,
            user_id=current_user.id,
            filename=filename,
            ass_id=ass_id,
        )


@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Delete an item.

    Args:
        item_id (int): The ID of the item to delete.
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        str: The result of the deletion.

    Raises:
        HTTPException: If the current user does not have enough permissions.
    """
    db_item = crud.get_item_by_id(db, item_id)
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not enough permissions")
    return crud.delete_item(db=db, item_id=item_id)


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Delete a user.

    Args:
        user_id (int): The ID of the user to delete.
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        str: The result of the deletion.

    Raises:
        HTTPException: If the current user does not have enough permissions.
    """
    if not crud.is_teacher(db, current_user.id) and user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not enough permissions")
    return crud.delete_user(db=db, user_id=user_id)


"""Assignment"""


@app.post("/create_assignment/")
async def create_assignment(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    assignment: schemas.AssignmentCreate,
    db: Session = Depends(get_db),
):
    """
    Create an assignment.

    Args:
        current_user (User): The current authenticated user.
        assignment (AssignmentCreate): The assignment data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Assignment: The created assignment.

    Raises:
        HTTPException: If the current user does not have enough permissions.
    """
    if crud.is_teacher(db, current_user.id):
        return crud.create_assignment(
            db=db, assignment=assignment, user_id=current_user.id
        )
    else:
        raise HTTPException(status_code=401, detail="Not enough permissions")


@app.get("/assignments/", response_model=list[schemas.Assignment])
def read_assignments(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Get a list of assignments.

    Args:
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[Assignment]: The list of assignments.
    """
    return crud.get_assignments(db=db)


@app.get("/users/me/assignments/", response_model=list[schemas.Assignment])
def read_own_assignments(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Get a list of users assignments.

    Args:
        current_user (User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[Assignment]: The list of assignments.
    """
    return crud.get_my_assignments(db=db, user_id=current_user.id)


@app.put("/update_assignment/{assignment_id}")
def update_assignment(
    assignment_id: int,
    description: str,
    github_url: str,
    filename: str,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Update an assignment with the given assignment ID.

    Args:
        assignment_id (int): The ID of the assignment to update.
        description (str): The updated description of the assignment.
        github_url (str): The GitHub URL of the assignment.
        filename (str): The updated filename of the assignment.
        current_user (schemas.User): The current authenticated user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        The updated assignment.

    Raises:
        HTTPException: If the current user does not have enough permissions to update the assignment.
    """
    ass_owner = crud.get_assignment_by_id(db=db, assignment_id=assignment_id).owner_id
    if current_user.id == ass_owner:
        return crud.update_assignment(
            db=db,
            assignment_id=assignment_id,
            description=description,
            github_url=github_url,
            filename=filename,
        )
    else:
        raise HTTPException(status_code=401, detail="Not enough permissions")


"""File upload"""


@app.post("/create_item/{ass_id}}")
async def create_upload_file(
    ass_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
):
    """
    Create and upload file for a given assignment ID.

    Parameters:
    - ass_id (int): The ID of the assignment.
    - current_user (schemas.User): The current authenticated user.
    - item (schemas.ItemCreate): The item to create.
    - db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - The created item.

    """
    return create_item(ass_id, item, current_user, db)


@app.post("/uploadfile/{ass_id}")
async def create_upload_file(
    ass_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    file: UploadFile = File(...),
):
    """
    Creates and upload file with the given assignment ID, current user, and file.

    Parameters:
        ass_id (int): The ID of the assignment.
        current_user (schemas.User): The current authenticated user.
        file (UploadFile): The file to be uploaded.

    Returns:
        dict: A dictionary containing the message indicating the success of the upload.
    """
    prefix = f"HW_{ass_id}_" + current_user.username
    if not file:
        return {"message": "No upload file sent"}
    else:
        file_extension = file.filename.split(".").pop()
        file_name = f"{prefix}.{file_extension}"
        with open(file_name, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"message": f"{file_name} has been uploaded successfully!"}


"""Run tests"""


@app.post("/test/{ass_id}")
async def run(
    ass_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Run the autograder for a given assignment.

    Parameters:
    - ass_id (int): The ID of the assignment.
    - current_user (schemas.User): The current authenticated user.
    - db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - dict: The result of the autograder.
    """

    resultfunc = run_tests(ass_id, current_user.username)
    passed = True if resultfunc["mark"] >= 50 else False
    crud.update_item(
        db=db,
        item_id=crud.get_item(db, f"HW_{ass_id}_{current_user.username}").id,
        tested=True,
        passed=passed,
        mark=resultfunc["mark"],
        pass_point=resultfunc["pass_points"],
        fail_point=resultfunc["failed_points"],
    ),

    return {"result": resultfunc}
