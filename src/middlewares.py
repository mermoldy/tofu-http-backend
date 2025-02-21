import base64
import functools
import time
import uuid

import fastapi
import structlog.contextvars
from starlette.middleware import base
from uvicorn.protocols import utils

from src import log
from src.config import config

__all__ = ["LogMiddleware"]

LOG_ACCESS = log.get_logger("api.access")
LOG_ERROR = log.get_logger("api.error")


@functools.lru_cache
def _build_auth_token() -> str:
    """Build the HTTP basic authentication token from config credentials."""
    return base64.b64encode(f"{config.username}:{config.password}".encode()).decode()


class LogMiddleware(base.BaseHTTPMiddleware):
    """The HTTP server access logging middleware."""

    async def dispatch(
        self, request: fastapi.Request, call_next: base.RequestResponseEndpoint
    ) -> fastapi.Response:
        start_time = time.monotonic()
        request_id = str(uuid.uuid4())[:8]

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = fastapi.Response(status_code=500)
        try:
            response = await call_next(request)
        except fastapi.HTTPException:
            LOG_ERROR.info("HTTP error.")
            raise
        except Exception:
            LOG_ERROR.exception("Server error.")
            raise
        finally:
            duration_ms = round((time.monotonic() - start_time) * 1000)
            status_code = response.status_code
            url = utils.get_path_with_query_string(request.scope)  # type: ignore[arg-type]
            client_host = request.client.host if request.client else "none"
            client_port = request.client.port if request.client else "none"
            http_method = request.method
            http_version = request.scope.get("http_version")

            LOG_ACCESS.info(
                f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
                http={
                    "request_id": request_id,
                    "url": str(request.url),
                    "status": status_code,
                    "method": http_method,
                    "version": http_version,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration_ms=duration_ms,
            )
            return response


class AuthnMiddleware(base.BaseHTTPMiddleware):
    """The HTTP basic authentication middleware."""

    async def dispatch(
        self, request: fastapi.Request, call_next: base.RequestResponseEndpoint
    ) -> fastapi.Response:
        if not ((h := request.headers.get("Authorization")) and h.startswith("Basic ")):
            return fastapi.Response(
                status_code=401, content="Unauthorized. Basic authentication required."
            )
        if h.removeprefix("Basic").strip() != _build_auth_token():
            return fastapi.Response(
                status_code=403, content="Forbidden. The username or password is incorrect."
            )
        return await call_next(request)
