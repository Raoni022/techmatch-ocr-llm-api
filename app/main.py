"""
AI Document Intelligence API

FastAPI backend prototype for document processing with OCR, lightweight NLP,
batch processing, query-based ranking, and audit logging boundaries.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.config import get_settings
from app.services.logging import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

settings = get_settings()
SERVICE_NAME = "AI Document Intelligence API"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting AI Document Intelligence API")
    logger.info("Environment: %s", settings.ENVIRONMENT)
    logger.info("Debug mode: %s", settings.DEBUG)
    yield
    logger.info("Stopping AI Document Intelligence API")


app = FastAPI(
    title=SERVICE_NAME,
    description="""
    ## Document intelligence backend prototype

    This API demonstrates OCR extraction, lightweight text analysis,
    information extraction, batch processing, query-based ranking, and audit
    logging boundaries for document-heavy workflows.

    ### Supported languages
    - Portuguese (`pt` / `por`)
    - English (`en` / `eng`)
    - Spanish (`es` / `spa`)

    ### Supported formats
    - PDF, TXT, DOC, DOCX, JPG, PNG
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={"name": "Raoni Medeiros", "url": "https://github.com/Raoni022"},
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
)

if settings.ALLOWED_HOSTS != "*":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[settings.ALLOWED_HOSTS])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ORIGINS == "*" else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global fallback for unhandled exceptions."""
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal server error occurred",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


app.include_router(router, prefix="/api/v1", tags=["API v1"])


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Return basic API metadata."""
    return {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "endpoints": {
            "health_check": "/api/v1/health",
            "text_analysis": "/api/v1/analyze-text",
            "file_upload": "/api/v1/upload",
            "batch_processing": "/api/v1/process-batch",
            "audit_logs": "/api/v1/audit-logs",
            "statistics": "/api/v1/stats",
        },
        "supported_languages": ["pt", "en", "es"],
        "supported_formats": ["PDF", "TXT", "DOC", "DOCX", "JPG", "PNG"],
    }


def create_app() -> FastAPI:
    """Factory function for tests and ASGI servers."""
    return app


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        server_header=False,
        date_header=False,
    )
