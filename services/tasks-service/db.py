from sqlmodel import create_engine, Session, SQLModel
from backend.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ECHO_DB_QUERIES,
    connect_args={}, # Add if needed, e.g., for SQLite: {"check_same_thread": False}
)

def get_session():
    """
    FastAPI dependency to get a database session.
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    Initializes the database and creates tables.
    Should be called once on application startup.
    """
    from backend import models  # Import models here to avoid circular imports
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully (if they didn't exist).")
