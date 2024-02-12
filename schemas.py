from pydantic import BaseModel


class ItemBase(BaseModel):
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int
    filename: str
    tested: bool | None = False
    passed: bool | None = False
    mark: int | None = 0
    pass_point: int | None = 0
    fail_point: int | None = 0

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    username: str
    role: str | None = "Student"


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool | None = True
    items: list[Item] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
