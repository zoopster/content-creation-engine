"""Content Creation Engine API - Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.routers import workflow, templates, content_types, platforms
from api.config import settings
from api.services.workflow_service import WorkflowService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Content Creation Engine API")
    # Initialize workflow service on startup
    app.state.workflow_service = WorkflowService()
    yield
    logger.info("Shutting down Content Creation Engine API")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(content_types.router, prefix="/api/content-types", tags=["content-types"])
app.include_router(platforms.router, prefix="/api/platforms", tags=["platforms"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "content-creation-engine",
        "version": settings.API_VERSION,
    }


@app.get("/api/output-formats")
async def list_output_formats():
    """List available output formats."""
    return {
        "formats": [
            {
                "id": "markdown",
                "name": "Markdown",
                "extension": ".md",
                "description": "Plain text with formatting syntax",
            },
            {
                "id": "html",
                "name": "HTML",
                "extension": ".html",
                "description": "Web-ready HTML document",
            },
            {
                "id": "docx",
                "name": "Word Document",
                "extension": ".docx",
                "description": "Microsoft Word format",
            },
            {
                "id": "pdf",
                "name": "PDF",
                "extension": ".pdf",
                "description": "Portable Document Format",
            },
            {
                "id": "pptx",
                "name": "PowerPoint",
                "extension": ".pptx",
                "description": "Microsoft PowerPoint presentation",
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
