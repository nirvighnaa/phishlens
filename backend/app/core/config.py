from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centralized application configuration.

    Values here can be overridden by environment variables (or a .env file)
    without touching code — this is how we'll handle secrets like API keys
    and database URLs later without ever committing them to Git.
    """

    APP_NAME: str = "PhishLens API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()