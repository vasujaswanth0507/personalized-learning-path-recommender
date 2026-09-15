import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "LearnPath"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # SQLite Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(BASE_DIR / "learnpath.db"))
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    
    # AI Engine Settings - Primary provider: Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Fallback to local heuristic/deterministic AI if no key is provided
    USE_LOCAL_FALLBACK_ON_ERROR: bool = True

settings = Settings()
