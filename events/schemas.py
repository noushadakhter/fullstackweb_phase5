from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel

class TaskData(BaseModel):
    # This should match the full task object schema from tasks-service
    # For now, a placeholder. Will be detailed during feature implementation.
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    completed: bool = False
    # Add other relevant fields from your task model

class TaskEvent(BaseModel):
    event_type: Literal["created", "updated", "completed", "deleted"]
    task_id: int
    task_data: TaskData # Full task object
    user_id: str
    timestamp: datetime = datetime.utcnow()

class ReminderEvent(BaseModel):
    task_id: int
    title: str
    due_at: datetime
    remind_at: datetime
    user_id: str
    timestamp: datetime = datetime.utcnow() # Add timestamp for consistency

class TaskUpdateEvent(BaseModel):
    # This event is for real-time sync, can be similar to TaskEvent but perhaps lighter
    event_type: Literal["created", "updated", "completed", "deleted"]
    task_id: int
    # task_data: TaskData # Can be included if full data is needed for updates
    user_id: str
    timestamp: datetime = datetime.utcnow()
    # For WebSocket updates, maybe just send minimal changes or ID for client to fetch
