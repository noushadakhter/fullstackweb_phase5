from sqlmodel import SQLModel
from typing import Optional

# Shared properties
class TodoBase(SQLModel):
    content: str
    is_completed: bool = False

# Properties to receive via API on creation
class TodoCreate(TodoBase):
    pass

# Properties to return via API
class TodoRead(TodoBase):
    id: int
    owner_id: int

# Properties to receive via API on update
class TodoUpdate(SQLModel):
    content: Optional[str] = None
    is_completed: Optional[bool] = None

# Shared properties
class UserBase(SQLModel):
    email: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return via API
class UserRead(UserBase):
    id: int

# JWT Token Schemas
class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None

# For chat input
class Message(SQLModel):
    content: str