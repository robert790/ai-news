"""AI News · central config.

Reads from .env via python-dotenv if installed. Falls back to safe defaults
if dotenv isn't installed or no .env exists, so the app still runs.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional — just read os.environ directly
    pass

# Paths
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
CHROMA_PATH = os.getenv("CHROMA_PATH", str(ROOT / "data" / "chroma"))

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# LLM endpoints (Groq is OpenAI-compatible, free tier is generous)
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.1-8b-instant"        # fast, free, great for summaries
GROQ_MODEL_LARGE = "llama-3.1-70b-versatile"  # slower, used for premium
ANTHROPIC_MODEL = "claude-sonnet-4-5"       # for premium tier

# App behavior
APP_LANGUAGE = os.getenv("APP_LANGUAGE", "ro")  # ro | en | both
NEWS_CACHE_HOURS = int(os.getenv("NEWS_CACHE_HOURS", "24"))
PREMIUM_ENABLED = os.getenv("PREMIUM_ENABLED", "false").lower() == "true"


def has_llm() -> bool:
    """True if any LLM API key is configured."""
    return bool(GROQ_API_KEY)


def has_anthropic() -> bool:
    return bool(ANTHROPIC_API_KEY)