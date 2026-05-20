import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import API_HOST, API_PORT, API_DEBUG, MODEL_NAME, BASE_URL
from app.api.router.comment_router import router as comment_router

logging.basicConfig(
    level=logging.DEBUG if API_DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Comment Generator",
    description="Generate AI-powered documentation comments for any programming language.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — allow VS Code extension and local dev tools ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "vscode-webview://*",
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(comment_router)


@app.get("/")
async def root():
    return {"status": "running", "service": "AI Comment Generator Backend"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint — confirms the service is running."""
    return {
        "status": "healthy",
        "service": "ai-comment-generator-backend",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "provider_url": BASE_URL,
    }


@app.on_event("startup")
async def on_startup():
    logger.info("═══════════════════════════════════════════════")
    logger.info("  AI Comment Generator Backend  v1.0.0")
    logger.info("  Model  : %s", MODEL_NAME)
    logger.info("  API    : http://%s:%d", API_HOST, API_PORT)
    logger.info("  Docs   : http://%s:%d/docs", API_HOST, API_PORT)
    logger.info("═══════════════════════════════════════════════")


if __name__ == "__main__":
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=API_DEBUG)
