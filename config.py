import os
from dotenv import load_dotenv

load_dotenv()

# ── API routing ──────────────────────────────────────────────────────────────
BASE_API_PREFIX = "/api/v1"

# ── LLM provider ─────────────────────────────────────────────────────────────
BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
API_KEY  = os.getenv("OPENROUTER_API_KEY", "")

# Model — override with LLM_MODEL env var for faster/different models.
# Good free options on OpenRouter:
#   "mistralai/mistral-7b-instruct:free"
#   "google/gemma-3-27b-it:free"
#   "meta-llama/llama-3.1-8b-instruct:free"
MODEL_NAME = os.getenv("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
MAX_TOKEN    = int(os.getenv("MAX_TOKEN", "800"))
TEMPERATURE  = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# ── Request timeouts ──────────────────────────────────────────────────────────
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
MAX_RETRIES     = int(os.getenv("MAX_RETRIES", "2"))

# ── Server ────────────────────────────────────────────────────────────────────
API_HOST  = os.getenv("API_HOST", "127.0.0.1")
API_PORT  = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"
