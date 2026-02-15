from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud, models, schemas
from app.database import get_session
from app.dependencies import get_current_user

# Dapr Integration
from dapr.clients import DaprClient
import json
from events.schemas import TaskEvent, ReminderEvent, TaskUpdateEvent, TaskData
import os # Needed for DAPR_GRPC_PORT and DAPR_HTTP_PORT

# Initialize Dapr Client
# DaprClient tries to connect to DAPR_GRPC_PORT and DAPR_HTTP_PORT
# If running outside Dapr, it won't connect and calls will fail
# For local testing, ensure Dapr is running (dapr run --app-id myapp ...)
# In K8s, Dapr sidecar automatically injects these env vars
DAPR_GRPC_PORT = os.getenv("DAPR_GRPC_PORT", "50001")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

dapr_client = DaprClient()

# Dapr PubSub component name (from dapr/components/pubsub-kafka.yaml)
PUBSUB_NAME = "pubsub-broker"

async def publish_event(topic: str, event: BaseModel):
    try:
        # Using DaprClient.publish_event for direct integration
        dapr_client.publish_event(
            pubsub_name=PUBSUB_NAME,
            topic_name=topic,
            data=json.dumps(event.dict()).encode('utf-8'),
            data_content_type="application/json",
        )
        print(f"Published event to topic '{topic}': {event.json()}")
    except Exception as e:
        print(f"Error publishing event to topic '{topic}': {e}")


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
    created_task = crud.create_todo_for_user(session=session, todo_in=task_in, owner_id=current_user.id)
    
    # Publish TaskEvent (created)
    task_event = TaskEvent(
        event_type="created",
        task_id=created_task.id,
        task_data=TaskData(**created_task.dict()), # Convert SQLModel to Pydantic TaskData
        user_id=current_user.id,
    )
    await publish_event("task-events", task_event)

    # Publish TaskUpdateEvent
    task_update_event = TaskUpdateEvent(
        event_type="created",
        task_id=created_task.id,
        user_id=current_user.id,
    )
    await publish_event("task-updates", task_update_event)

    return created_task

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
    
    updated_task = crud.update_todo(session=session, todo=task, todo_in=task_in)

    # Publish TaskEvent (updated)
    task_event = TaskEvent(
        event_type="updated",
        task_id=updated_task.id,
        task_data=TaskData(**updated_task.dict()),
        user_id=current_user.id,
    )
    await publish_event("task-events", task_event)

    # Publish TaskUpdateEvent
    task_update_event = TaskUpdateEvent(
        event_type="updated",
        task_id=updated_task.id,
        user_id=current_user.id,
    )
    await publish_event("task-updates", task_update_event)

    # Check for ReminderEvent if due_date is set or updated
    if updated_task.due_date and (not task.due_date or updated_task.due_date != task.due_date):
        reminder_event = ReminderEvent(
            task_id=updated_task.id,
            title=updated_task.title,
            due_at=updated_task.due_date,
            remind_at=updated_task.due_date, # For now, remind_at is same as due_at
            user_id=current_user.id,
        )
        await publish_event("reminders", reminder_event)

    return updated_task

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
        
    # Publish TaskEvent (deleted) before actual deletion
    task_event = TaskEvent(
        event_type="deleted",
        task_id=task.id,
        task_data=TaskData(**task.dict()), # Send the task data before it's gone
        user_id=current_user.id,
    )
    await publish_event("task-events", task_event)

    # Publish TaskUpdateEvent
    task_update_event = TaskUpdateEvent(
        event_type="deleted",
        task_id=task.id,
        user_id=current_user.id,
    )
    await publish_event("task-updates", task_update_event)

    crud.delete_todo(session=session, todo=task)
    return
