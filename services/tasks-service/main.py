from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session

from backend.app.database import create_db_and_tables, get_session
from backend.models import Task, Conversation, Message # Import models if needed for type hints or initial testing
from backend.app.api.endpoints import chat # Import the chat router

app = FastAPI(
    title="Todo AI Chatbot Backend",
    version="0.1.0",
)

@app.on_event("startup")
def on_startup():
    print("Creating database tables if they don't exist...")
    create_db_and_tables()
    print("Database tables created.")

app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is healthy"}

# Example of a protected endpoint (will be integrated with Better Auth later)
@app.get("/protected", status_code=status.HTTP_200_OK)
def protected_route(session: Session = Depends(get_session)):
    return {"message": "This is a protected route!"}