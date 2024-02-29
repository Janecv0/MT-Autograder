from pydantic import BaseModel, EmailStr

class RoleBase(BaseModel):
    """
    Base model for a role.
    """

    name: str
    slug: str | None = None
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
    roles: list[RoleBase] = []
    own_assignments: list | None

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
    pass


class Assignment(AssignmentBase):
    """
    Model for an assignment.
    """

    id: int
    owner_id: int
    items: list[Item] = []
    classroom_id: int

    class Config:
        """
        Configuration for the Assignment model.
        """

        from_attributes = True


class ClassroomBase(BaseModel):
    """
    Base model for a classroom.
    """

    name: str
    description: str | None = None
    year: int


class ClassroomCreate(ClassroomBase):
    """
    Model for creating a classroom.
    """

    pass


class Classroom(ClassroomBase):
    """
    Model for a classroom.
    """

    id: int
    owner_id: int
    owner: User
    assignments: list[Assignment] = []
    students: list[User] = []

    class Config:
        """
        Configuration for the Classroom model.
        """

        from_attributes = True


class EmailSchema(BaseModel):
    """
    Model for an email.
    """

    email: list[EmailStr]
