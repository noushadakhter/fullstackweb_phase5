# backend/routes/tasks.py
from datetime import datetime
from typing import List
from uuid import UUID # Import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import auth
import models
import schemas
from db import get_session

router = APIRouter(
    prefix="/api/{user_id}/tasks",
    tags=["tasks"],
    dependencies=[Depends(auth.verify_user_access)],
)

# Helper to validate user_id from path against authenticated user
def _validate_user_id(path_user_id: str, current_user: auth.User):
    try:
        if UUID(path_user_id) != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access tasks for this user ID",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

@router.get("", response_model=List[schemas.TaskResponse])
def get_tasks(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: auth.User = Depends(auth.get_current_user), # Add current_user dependency
):
    _validate_user_id(user_id, current_user)
    tasks = session.exec(select(models.TodoItem).where(models.TodoItem.owner_id == current_user.id)).all()
    return tasks


@router.post("", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: str,
    task: schemas.TaskCreate,
    session: Session = Depends(get_session),
    current_user: auth.User = Depends(auth.get_current_user), # Add current_user dependency
):
    _validate_user_id(user_id, current_user)
    new_task = models.TodoItem(**task.dict(), owner_id=current_user.id) # Use owner_id
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@router.get("/{id}", response_model=schemas.TaskResponse)
def get_task(
    user_id: str,
    id: UUID, # Change to UUID
    session: Session = Depends(get_session),
    current_user: auth.User = Depends(auth.get_current_user), # Add current_user dependency
):
    _validate_user_id(user_id, current_user)
    task = session.exec(
        select(models.TodoItem).where(models.TodoItem.id == id, models.TodoItem.owner_id == current_user.id)
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{id}", response_model=schemas.TaskResponse)
def update_task(
    user_id: str,
    id: UUID, # Change to UUID
    task_update: schemas.TaskUpdate,
    session: Session = Depends(get_session),
    current_user: auth.User = Depends(auth.get_current_user), # Add current_user dependency
):
    _validate_user_id(user_id, current_user)
    task = session.exec(
        select(models.TodoItem).where(models.TodoItem.id == id, models.TodoItem.owner_id == current_user.id)
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: str,
    id: UUID, # Change to UUID
    session: Session = Depends(get_session),
    current_user: auth.User = Depends(auth.get_current_user), # Add current_user dependency
):
    _validate_user_id(user_id, current_user)
    task = session.exec(
        select(models.TodoItem).where(models.TodoItem.id == id, models.TodoItem.owner_id == current_user.id)
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    session.delete(task)
    session.commit()


@router.patch("/{id}/complete", response_model=schemas.TaskResponse)
def mark_task_complete(
    user_id: str,
    id: UUID, # Change to UUID
    session: Session = Depends(get_session),
    current_user: auth.User = Depends(auth.get_current_user), # Add current_user dependency
):
    _validate_user_id(user_id, current_user)
    task = session.exec(
        select(models.TodoItem).where(models.TodoItem.id == id, models.TodoItem.owner_id == current_user.id)
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.completed = True
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task