from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str

class UserPublic(BaseModel):
    id: UUID
    email: str

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str

# New Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True