import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router.comment_router import (
    router as comment_router,
)
from config import (
    API_DEBUG,
    API_HOST,
    API_PORT,
    BASE_URL,
    MODEL_NAME,
)

# ─────────────────────────────────────────────────────────────
# Logging Configuration
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if API_DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Comment Generator",
    description=(
        "Generate AI-powered documentation comments "
        "for multiple programming languages."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────
# CORS Configuration
# ─────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────

app.include_router(comment_router)

# ─────────────────────────────────────────────────────────────
# Root Endpoint
# ─────────────────────────────────────────────────────────────


@app.api_route(
    "/",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
async def root():

    return {
        "status": "running",
        "service": "AI Comment Generator Backend",
    }


# ─────────────────────────────────────────────────────────────
# Health Check Endpoint
# ─────────────────────────────────────────────────────────────


@app.api_route(
    "/health",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
async def health_check():

    return {
        "status": "healthy",
        "service": "ai-comment-generator-backend",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "provider_url": BASE_URL,
    }


# ─────────────────────────────────────────────────────────────
# Startup Event
# ─────────────────────────────────────────────────────────────


@app.on_event("startup")
async def on_startup():

    logger.info("═══════════════════════════════════════════════")

    logger.info("  AI Comment Generator Backend v1.0.0")

    logger.info(
        "  Model : %s",
        MODEL_NAME,
    )

    logger.info(
        "  Provider : %s",
        BASE_URL,
    )

    logger.info("═══════════════════════════════════════════════")


# ─────────────────────────────────────────────────────────────
# Local Development Entry Point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG,
    )
