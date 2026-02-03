"""
Main FastAPI application for OpenUser Digital Human System.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.voice import router as voice_router
from src.api.auth import router as auth_router, set_db_manager
from src.api.digital_human import router as digital_human_router
from src.api.plugins import router as plugins_router
from src.api.agents import router as agents_router
from src.api.scheduler import router as scheduler_router
from src.api.websocket import router as websocket_router
from src.models.base import DatabaseManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./openuser.db")
    db_manager = DatabaseManager(database_url, echo=False)
    db_manager.create_tables()
    set_db_manager(db_manager)
    print(f"Database initialized: {database_url}")

    yield

    # Shutdown: cleanup if needed
    print("Application shutting down")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="OpenUser API",
        description="Intelligent Digital Human System API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router)
    app.include_router(voice_router)
    app.include_router(digital_human_router)
    app.include_router(plugins_router)
    app.include_router(agents_router)
    app.include_router(scheduler_router)
    app.include_router(websocket_router)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "OpenUser API",
            "version": "0.1.0",
            "docs": "/docs"
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create app instance
app = create_app()
