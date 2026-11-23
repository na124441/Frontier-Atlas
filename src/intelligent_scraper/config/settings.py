"""
Centralized Configuration Management.
Reads settings from environment variables or .env file with sensible defaults.
"""

from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "Intelligent Web Scraper"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database & Storage
    # Default to SQLite for seamless zero-setup local dev/testing, supports PostgreSQL
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/scraper.db",
        description="Async database connection URL (PostgreSQL or SQLite)"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for task queues and locking"
    )
    USE_IN_MEMORY_FALLBACK: bool = Field(
        default=True,
        description="Fallback to in-memory queue/cache if Redis is unavailable"
    )

    # Concurrency & Network Limits
    MAX_CONCURRENT_REQUESTS: int = 50
    HTTP_TIMEOUT: int = 30
    BROWSER_TIMEOUT: int = 45
    REQUEST_DELAY_SECONDS: float = 0.5
    MAX_RETRIES: int = 5
    BACKOFF_BASE_SECONDS: float = 1.0
    BACKOFF_MAX_SECONDS: float = 60.0

    # Freshness
    FRESHNESS_HOURS: int = 24

    # Target record thresholds (Assessment requirements)
    TARGET_STARTUPS: int = 1000
    TARGET_PRODUCTS: int = 1000
    TARGET_RESEARCH_PAPERS: int = 1000

    # LLM Providers & Credentials
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GROQ_API_KEY: str = Field(default="", description="Groq API Key")
    DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API Key")

    # LLM Models & Behavior
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GROQ_MODEL: str = "llama3-70b-8192"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    LLM_PROVIDER_PRIORITY: List[str] = Field(
        default_factory=lambda: ["gemini", "groq", "deepseek"]
    )
    CHUNK_SIZE_TOKENS: int = 3500
    CHUNK_OVERLAP_TOKENS: int = 200

    # GitHub API
    GITHUB_TOKEN: str = Field(default="", description="Optional GitHub Personal Access Token")

    # Google Sheets Export
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = Field(default="", description="Path to service_account.json")
    GOOGLE_SHEETS_SPREADSHEET_ID: str = Field(default="", description="Google Sheet ID to update")
    EXPORT_DIR: str = Field(default="./data/processed", description="Local export directory fallback")

    # Data Seed Paths
    SEED_DATABASE_PATH: str = Field(default="./data/seed/ai_startups_seed.json")
    SOURCES_CONFIG_PATH: str = Field(default="./configs/sources.yaml")
    EXTRACTION_RULES_PATH: str = Field(default="./configs/extraction_rules.yaml")


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton instance."""
    return Settings()


settings = get_settings()
