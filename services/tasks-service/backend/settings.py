from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    DATABASE_URL: str
    OPENAI_API_KEY: str
    MCP_SERVER_URL: str
    ECHO_DB_QUERIES: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
