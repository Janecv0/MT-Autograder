from pydantic import BaseModel


class ItemBase(BaseModel):
    """
    Base model for an item.
    """

    description: str | None = None
    assignment_id: int


class ItemCreate(ItemBase):
    """
    Model for creating an item.
    """


class Item(ItemBase):
    """
    Model for an item.
    """

    id: int
    owner_id: int
    filename: str
    tested: bool | None = False
    passed: bool | None = False
    mark: float | None = 0
    pass_point: int | None = 0
    fail_point: int | None = 0

    class Config:
        """
        Configuration for the Item model.
        """

        from_attributes = True


class UserBase(BaseModel):
    """
    Base model for a user.
    """

    email: str
    username: str
    role: str | None = "Student"


class UserCreate(UserBase):
    """
    Model for creating a user.
    """

    password: str


class User(UserBase):
    """
    Model for a user.
    """

    id: int
    is_active: bool | None = True
    items: list[Item] = []

    class Config:
        """
        Configuration for the User model.
        """

        from_attributes = True


class Token(BaseModel):
    """
    Model for a token.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Model for token data.
    """

    username: str | None = None


class AssignmentBase(BaseModel):
    """
    Base model for an assignment.
    """

    description: str | None = None
    github_url: str | None = None
    filename: str


class AssignmentCreate(AssignmentBase):
    """
    Model for creating an assignment.
    """


class Assignment(AssignmentBase):
    """
    Model for an assignment.
    """

    id: int
    owner_id: int

    class Config:
        """
        Configuration for the Assignment model.
        """

        from_attributes = True
