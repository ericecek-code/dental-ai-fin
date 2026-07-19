from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Dental AI"
    version: str = "0.1.0"
    upload_max_size_mb: int = 50
    default_confidence: float = 0.5
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
