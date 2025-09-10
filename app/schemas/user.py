from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows SQLAlchemy models -> Pydantic

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserOut(UserBase):
    id: UUID

    class Config:
        from_attributes = True