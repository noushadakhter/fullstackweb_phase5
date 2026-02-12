from typing import Optional, List
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, Relationship, create_engine
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class TaskBase(SQLModel):
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional: Link back to user/conversation if needed, but per spec, it's tied to user_id
    # messages: List["Message"] = Relationship(back_populates="task") # If messages could be tied to tasks

class ConversationBase(SQLModel):
    user_id: str = Field(index=True)

class Conversation(ConversationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    messages: List["Message"] = Relationship(back_populates="conversation")

class MessageBase(SQLModel):
    user_id: str = Field(index=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: Role
    content: str

class Message(MessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    conversation: Optional[Conversation] = Relationship(back_populates="messages")

# This part is for database connection, normally in a separate db.py
# Example placeholder for engine, will be properly configured in db.py
# engine = create_engine("sqlite:///database.db") 

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)