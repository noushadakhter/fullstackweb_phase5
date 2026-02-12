from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for local development if .env is not set up
    # In production, DATABASE_URL must be set.
    print("DATABASE_URL not found in environment variables, using SQLite for local development.")
    DATABASE_URL = "sqlite:///./database.db"

# Create the engine
# For PostgreSQL, use "postgresql+psycopg2://"
# For SQLite, use "sqlite:///"
engine = create_engine(DATABASE_URL, echo=True) # echo=True for logging SQL statements

def create_db_and_tables():
    """Create all tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session