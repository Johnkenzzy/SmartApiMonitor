import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from secure import Secure
import structlog

from app.config import settings
from app.db import init_db
from app.api import routes_auth

# --- Logging Setup ---
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=settings.LOG_LEVEL,
)

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# --- Security Headers ---
secure_headers = Secure()

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Update response headers with secure defaults
        response.headers.update(secure_headers.headers)
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
    )

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"] if settings.DEBUG else [],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # --- Security Headers Middleware ---
    app.add_middleware(SecureHeadersMiddleware)

    # --- Include Routers ---
    app.include_router(routes_auth.router, prefix="/auth", tags=["Auth"])

    # --- Startup/Shutdown events ---
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Application startup", environment=settings.ENVIRONMENT)
        init_db()  # create all tables

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("🛑 Application shutdown")

    return app


app = create_app()
