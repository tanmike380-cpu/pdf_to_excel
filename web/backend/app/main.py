"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.api.routes_parse import router as parse_router
from app.api.routes_download import router as download_router
from app.services.cleanup_service import schedule_cleanup_task
from app.core.logger import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting up...")
    schedule_cleanup_task()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="PDF to Excel API",
    description="Extract structured data from PDFs and images",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(parse_router, tags=["Parse"])
app.include_router(download_router, tags=["Download"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PDF to Excel API", "docs": "/docs"}
