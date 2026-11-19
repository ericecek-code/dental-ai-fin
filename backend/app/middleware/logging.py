"""
Structured request logging middleware.

Loguje každý request s: metódou, cestou, status kódom, časom spracovania a client IP.
Používateľské dáva (telo requestu, súbory) sa nelogujú kvôli GDPR a bezpečnosti.
HTTPException sa nechá prejsť (re-raise), aby FastAPI správne vygeneroval chybovú odpoveď.
"""

import time
import logging
from fastapi import Request
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("dental-ai")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        # Client IP (zohľadňuje proxy)
        client_ip = request.client.host if request.client else "unknown"
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()

        path = request.url.path
        method = request.method

        try:
            response = await call_next(request)
            process_time = (time.perf_counter() - start) * 1000  # ms

            logger.info(
                f"{method} {path} -> {response.status_code} "
                f"({process_time:.1f}ms) ip={client_ip}"
            )
            return response
        except HTTPException:
            # Nechaj HTTPException prejsť bez zabalenia do Exception Group
            process_time = (time.perf_counter() - start) * 1000
            logger.warning(
                f"{method} {path} -> HTTPException ({process_time:.1f}ms) ip={client_ip}"
            )
            raise
        except Exception as exc:
            process_time = (time.perf_counter() - start) * 1000
            logger.exception(
                f"{method} {path} -> ERROR {exc!s} "
                f"({process_time:.1f}ms) ip={client_ip}"
            )
            raise