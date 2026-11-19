"""
Authentication middleware for Dental AI API.

Podporuje dva spôsoby overenia:
1) API Key v hlavičke: X-API-Key: <token>
2) Bearer token: Authorization: Bearer <token>

Ak je nastavené API_TOKEN v .env, vyžaduje sa overenie na našich API endpointoch
(/analyze, /results, /history, /vision, /ws). Verejné a interné cesty sú bez auth.
"""

import hmac

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

# Cesty, ktoré nikdy nevyžadujú auth (health, docs, interné FastAPI, static)
PUBLIC_PATHS = {
    "/",
    "/health",
    "/health/v1",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
    "/v1/models",  # interný endpoint (napr. niektorý AI provider client)
}

PUBLIC_PREFIXES = (
    "/static",
    "/assets",
)

# Naše API cesty, na ktoré aplikujeme auth (ak je nastavené API_TOKEN)
API_PREFIXES = (
    "/analyze",
    "/results",
    "/history",
    "/vision",
    "/ws",
)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_token: str | None = None):
        super().__init__(app)
        self.api_token = api_token

    async def dispatch(self, request: Request, call_next):
        # Ak nie je nastavené API_TOKEN, auth je vypnuté (dev módu)
        if not settings.api_token_active:
            return await call_next(request)

        path = request.url.path

        # Verejné cesty – preskočíme auth
        if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)

        # Ak cesta nepatrí k našim API endpointom, preskočíme auth (interné FastAPI cesty, atď.)
        if not path.startswith(API_PREFIXES):
            return await call_next(request)

        # Overenie API Key alebo Bearer token
        api_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization", "")

        token = None
        if api_key:
            token = api_key
        elif auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]

        if not token or not hmac.compare_digest(token, settings.api_token or ""):
            # BaseHTTPMiddleware neprekladá HTTPException na odpoveď — vrátime JSON priamo.
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing or invalid API token. "
                    "Use X-API-Key header or Authorization: Bearer <token>"
                },
            )

        return await call_next(request)