from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import Session, select

from backend.models import Task, Conversation, Message, Role

# --- CRUD Operations for Task ---

def create_task(session: Session, user_id: str, title: str, description: Optional[str] = None) -> Task:
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_task(session: Session, task_id: int, user_id: str) -> Optional[Task]:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    return session.exec(statement).first()

def get_tasks(session: Session, user_id: str, status: str = "all") -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    if status == "pending":
        statement = statement.where(Task.completed == False)
    elif status == "completed":
        statement = statement.where(Task.completed == True)
    return session.exec(statement).all()

def update_task(
    session: Session,
    task_id: int,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> Optional[Task]:
    task = get_task(session, task_id, user_id)
    if task:
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed

        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

    return task

def delete_task(session: Session, task_id: int, user_id: str) -> Optional[Task]:
    task = get_task(session, task_id, user_id)
    if task:
        session.delete(task)
        session.commit()
    return task

# --- CRUD Operations for Conversation ---

def create_conversation(session: Session, user_id: str) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

def get_conversation(session: Session, conversation_id: int, user_id: str) -> Optional[Conversation]:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    return session.exec(statement).first()

# --- CRUD Operations for Message ---

def create_message(
    session: Session,
    user_id: str,
    conversation_id: int,
    role: Role,
    content: str
) -> Message:
    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

def get_messages_for_conversation(
    session: Session,
    conversation_id: int,
    user_id: str
) -> List[Message]:
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at)
    )
    return session.exec(statement).all()
