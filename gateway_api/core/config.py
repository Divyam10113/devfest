from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages all application settings.
    Automatically reads variables from the .env file.
    """
    # Database settings
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    MAX_FAILED_ATTEMPTS: int
    LOCKOUT_DURATION_SECONDS: int

    HEARTBEAT_INTERVAL_SECONDS: int

    OPENAI_API_KEY: str
    VECTOR_DB_URL: str = "http://ingestion-service:8002"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",       # Ignores extra variables in .env
        case_sensitive=False  # Allows matching 'database_url' to 'DATABASE_URL'
    )

settings = Settings()