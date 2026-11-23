"""
Domain enumerations for Intelligent Web Scraper.
"""

from enum import Enum


class RecordType(str, Enum):
    STARTUP = "STARTUP"
    PRODUCT = "PRODUCT"
    RESEARCH_PAPER = "RESEARCH_PAPER"
    JOB = "JOB"
    NEWS = "NEWS"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"


class SourceCategory(str, Enum):
    STARTUP_DIRECTORY = "startup_directory"
    PRODUCT_DIRECTORY = "product_directory"
    RESEARCH_REPOSITORY = "research_repository"
    GITHUB_REPOSITORY = "github_repository"
    NEWS_WEBSITE = "news_website"
    JOB_BOARD = "job_board"


class PricingModel(str, Enum):
    FREE = "FREE"
    FREEMIUM = "FREEMIUM"
    PAID = "PAID"
    ENTERPRISE = "ENTERPRISE"


class CrawlStrategy(str, Enum):
    HTTP = "http"
    BROWSER = "browser"
    API = "api"
    ADAPTIVE = "adaptive"


class LLMProviderName(str, Enum):
    GEMINI = "gemini"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    MOCK = "mock"
