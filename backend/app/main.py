import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.controllers.router import api_router
from app.core.config import get_settings
from app.core.correlation import RequestIDMiddleware, get_request_id
from app.core.logging import configure_logging
from app.persistence.session import engine
from app.models import Deployment, Incident, IncidentEvent, InvestigationRun, LogEntry  # noqa: F401

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("opspilot")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title="OpsPilot API",
    version="0.3.0",
    description="AI-powered SRE / Incident Intelligence platform API",
    lifespan=lifespan,
)

# Request ID / Correlation ID Middleware must be added first
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    req_id = get_request_id()
    logger.info(
        "request received",
        extra={"request_path": request.url.path, "method": request.method, "request_id": req_id},
    )
    response = await call_next(request)
    logger.info(
        "request completed",
        extra={
            "request_path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "request_id": req_id,
        },
    )
    return response


@app.exception_handler(HTTPException)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    req_id = get_request_id()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "request_id": req_id,
        },
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    req_id = get_request_id()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request payload validation failed",
            "code": "VALIDATION_ERROR",
            "errors": exc.errors(),
            "request_id": req_id,
        },
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    req_id = get_request_id()
    logger.exception("unhandled runtime exception", extra={"request_path": request.url.path, "request_id": req_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "code": "INTERNAL_SERVER_ERROR",
            "request_id": req_id,
        },
        headers={"X-Request-ID": req_id},
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/docs"}
