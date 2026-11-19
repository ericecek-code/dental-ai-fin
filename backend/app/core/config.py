"""
Pydantic-based settings for Dental AI.

Načítava premenné z .env (ak existuje) alebo z prostredia.
Produkcia: nastavte API_TOKEN, CORS_ORIGINS, LOG_LEVEL pomocou env premenných.
"""

import tempfile
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ — všetky relatívne cesty sa odvodzujú odtiaľto, nie od cwd.
BASE_DIR = Path(__file__).resolve().parents[2]

# Hodnoty, ktoré v .env znamenajú "token nie je nastavený".
_TOKEN_PLACEHOLDERS = {
    "replace-with-secure-token-in-production",
    "replace-with-generated-token",
    "changeme",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Aplikácia ---
    app_name: str = "Dental AI"
    version: str = "0.1.0"

    # --- Upload ---
    upload_max_size_mb: int = 50

    # --- Model ---
    default_confidence: float = 0.05
    model_path: str = str(BASE_DIR / "weights" / "yolov8x_dental.pt")

    # --- Runtime dáta (uploady, výstupy, reporty, SQLite) ---
    data_dir: str = str(Path(tempfile.gettempdir()) / "dental-ai")

    # --- CORS — produkcia: konkrétne domény, nie wildcard ---
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ]

    # --- Bezpečnosť ---
    # Nastavte v produkcii silný náhodný reťazec, napr.: API_TOKEN=sk_live_...
    api_token: str | None = None

    # --- Gemini Vision (voliteľné, bez kľúča sa /vision vráti s chybou) ---
    gemini_api_key: str | None = None

    # --- Logovanie ---
    log_level: str = "INFO"

    @property
    def api_token_active(self) -> bool:
        """True len ak je API_TOKEN reálne nastavený (nie placeholder)."""
        token = (self.api_token or "").strip()
        return bool(token) and token not in _TOKEN_PLACEHOLDERS

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)

    @property
    def weights_path(self) -> Path:
        path = Path(self.model_path)
        return path if path.is_absolute() else BASE_DIR / path

    @property
    def static_path(self) -> Path:
        """Priečinok s zabudovaným frontend buildom (index.html + assets/)."""
        return BASE_DIR / "static"


settings = Settings()
