from sqlmodel import Session, select
from typing import List, Optional

from backend.models import Task
from backend.db import engine

# A simple error class
class TaskNotFoundError(Exception):
    pass

# ===============================================
# MCP TOOL IMPLEMENTATIONS
# ===============================================

def add_task(user_id: int, title: str, description: Optional[str] = None) -> dict:
    """Creates a new to-do task for a specified user."""
    with Session(db.engine) as session:
        new_task = models.Task(
            user_id=user_id,
            title=title,
            description=description
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task.dict()

def list_tasks(user_id: int, status: str = "all") -> List[dict]:
    """Retrieves a list of to-do tasks for a specified user."""
    with Session(db.engine) as session:
        statement = select(models.Task).where(models.Task.user_id == user_id)
        
        if status == "pending":
            statement = statement.where(models.Task.completed == False)
        elif status == "completed":
            statement = statement.where(models.Task.completed == True)
        
        tasks = session.exec(statement).all()
        return [task.dict() for task in tasks]

def complete_task(user_id: int, task_id: int) -> dict:
    """Marks an existing task as completed."""
    with Session(db.engine) as session:
        task = session.exec(
            select(models.Task).where(models.Task.id == task_id, models.Task.user_id == user_id)
        ).first()

        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found for user {user_id}")

        task.completed = True
        session.add(task)
        session.commit()
        session.refresh(task)
        return task.dict()

def update_task(user_id: int, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> dict:
    """Updates the title and/or description of an existing task."""
    with Session(db.engine) as session:
        task = session.exec(
            select(models.Task).where(models.Task.id == task_id, models.Task.user_id == user_id)
        ).first()

        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found for user {user_id}")

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        
        session.add(task)
        session.commit()
        session.refresh(task)
        return task.dict()

def delete_task(user_id: int, task_id: int) -> dict:
    """Deletes an existing task."""
    with Session(db.engine) as session:
        task = session.exec(
            select(models.Task).where(models.Task.id == task_id, models.Task.user_id == user_id)
        ).first()

        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found for user {user_id}")

        session.delete(task)
        session.commit()
        return {"success": True, "deleted_task_id": task_id}


# ===============================================
# MCP SERVER SETUP
# ===============================================

# Placeholder for MCP SDK server setup.
# This will be filled in once the official MCP SDK is available or mocked.
def run_mcp_server():
    """
    This function will configure and run the MCP server,
    registering the tool functions.
    """
    print("MCP Server running...")
    # Example of how it might look:
    # from mcp_sdk import MCP_Server
    # server = MCP_Server()
    # server.register_tool("add_task", add_task)
    # server.register_tool("list_tasks", list_tasks)
    # ... register other tools ...
    # server.run()

if __name__ == "__main__":
    run_mcp_server()