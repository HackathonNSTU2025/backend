from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    image: str
    created_at: datetime
