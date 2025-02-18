import time
import uuid

import fastapi
import structlog.contextvars
from starlette.middleware import base
from uvicorn.protocols import utils

from src import log

__all__ = ["LogMiddleware"]

LOG_ACCESS = log.get_logger("api.access")
LOG_ERROR = log.get_logger("api.error")


class LogMiddleware(base.BaseHTTPMiddleware):
    """The HTTP server access logging middleware."""

    async def dispatch(self, request: fastapi.Request, call_next) -> fastapi.Response:
        start_time = time.perf_counter_ns()
        request_id = str(uuid.uuid4())[:8]

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = fastapi.Response(status_code=500)
        try:
            response = await call_next(request)
        except Exception:
            LOG_ERROR.exception("Server error.")
            raise
        finally:
            process_time = time.perf_counter_ns() - start_time
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
                duration=process_time,
            )
            response.headers["X-Process-Time"] = str(process_time / 10**9)
            return response
