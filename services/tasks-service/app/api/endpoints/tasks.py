from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/tasks", response_model=List[schemas.TodoRead])
def read_tasks(
    *,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve all tasks for the current user.
    """
    return crud.get_todos_by_owner(session=session, owner_id=current_user.id)

@router.post("/tasks", response_model=schemas.TodoRead, status_code=status.HTTP_201_CREATED)
def create_task(
    *,
    session: Session = Depends(get_session),
    task_in: schemas.TodoCreate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Create a new task for the current user.
    """
    return crud.create_todo_for_user(session=session, todo_in=task_in, owner_id=current_user.id)

@router.put("/tasks/{task_id}", response_model=schemas.TodoRead)
def update_task(
    *,
    session: Session = Depends(get_session),
    task_id: int,
    task_in: schemas.TodoUpdate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Update a task for the current user.
    """
    task = crud.get_todo_by_id(session=session, todo_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return crud.update_todo(session=session, todo=task, todo_in=task_in)

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    *,
    session: Session = Depends(get_session),
    task_id: int,
    current_user: models.User = Depends(get_current_user),
):
    """
    Delete a task for the current user.
    """
    task = crud.get_todo_by_id(session=session, todo_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    crud.delete_todo(session=session, todo=task)
    return
