import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")

_STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
    429: "rate_limited",
}


class AppError(Exception):
    """A deliberate, client-visible failure raised by services and dependencies."""

    def __init__(self, status_code: int, code: str, message: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers = headers


def _envelope(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[dict] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": getattr(request.state, "request_id", None),
        }
    }
    return JSONResponse(status_code=status_code, content=body, headers=headers)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return _envelope(request, exc.status_code, exc.code, exc.message, headers=exc.headers)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = _STATUS_CODES.get(exc.status_code, f"http_{exc.status_code}")
    return _envelope(request, exc.status_code, code, str(exc.detail), headers=exc.headers)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Only loc/msg/type are returned: never echo the submitted input (it may contain a password).
    details = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return _envelope(request, 422, "validation_error", "Request validation failed.", details)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the real error server-side; never leak internals to the client.
    logger.exception("unhandled_exception", extra={"request_id": getattr(request.state, "request_id", None)})
    return _envelope(request, 500, "internal_error", "An unexpected error occurred.")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
