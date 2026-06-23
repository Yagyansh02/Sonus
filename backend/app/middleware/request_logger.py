"""
Request logging middleware.

Logs every incoming request with method, path, status code,
and response time for observability.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import get_logger

logger = get_logger("middleware.request_logger")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware that logs request/response metrics for every API call."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log the request
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} "
            f"({duration_ms:.1f}ms)"
        )

        # Add timing header for debugging
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"

        return response
