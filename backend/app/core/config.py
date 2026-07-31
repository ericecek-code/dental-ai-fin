from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Dental AI"
    version: str = "0.1.0"

    # --- Upload ---
    upload_max_size_mb: int = 50

    # --- Model ---
    default_confidence: float = 0.05

    # --- CORS ---
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ]

    # --- Bezpečnosť ---
    api_token: str | None = None

    # --- Logovanie ---
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
