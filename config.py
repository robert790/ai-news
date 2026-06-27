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
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# LLM endpoints (DeepSeek is OpenAI-compatible)
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"            # V3, cheap + good
DEEPSEEK_REASONER_MODEL = "deepseek-reasoner"  # R1, for hard analysis
ANTHROPIC_MODEL = "claude-sonnet-4-5"       # for premium tier

# App behavior
APP_LANGUAGE = os.getenv("APP_LANGUAGE", "ro")  # ro | en | both
NEWS_CACHE_HOURS = int(os.getenv("NEWS_CACHE_HOURS", "24"))
PREMIUM_ENABLED = os.getenv("PREMIUM_ENABLED", "false").lower() == "true"


def has_deepseek() -> bool:
    return bool(DEEPSEEK_API_KEY)


def has_anthropic() -> bool:
    return bool(ANTHROPIC_API_KEY)