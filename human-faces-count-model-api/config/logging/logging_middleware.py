# app/middleware/logging_middleware.py
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log the incoming request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"➡️  {request.method} {request.url.path} from {client_ip}")

        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exceptions with traceback
            logger.exception(f"❌ Exception during request {request.method} {request.url.path}: {exc}")
            raise

        process_time = (time.time() - start_time) * 1000  # ms
        logger.info(
            f"⬅️  {request.method} {request.url.path} "
            f"completed with status {response.status_code} "
            f"in {process_time:.2f}ms"
        )

        # Optionally add timing header for debugging
        response.headers["X-Process-Time-ms"] = f"{process_time:.2f}"
        return response
