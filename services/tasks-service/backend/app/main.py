from fastapi import FastAPI
from app.database import create_db_and_tables
from app.api.endpoints import auth, tasks, chat

app = FastAPI(title="Todo AI Chatbot")

# Create database and tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo AI Chatbot API"}
