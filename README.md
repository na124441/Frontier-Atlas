# Intelligent Web Scraping & AI-Powered Data Intelligence Platform

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI/AsyncIO](https://img.shields.io/badge/Runtime-asyncio-009688.svg?style=flat)](https://docs.python.org/3/library/asyncio.html)
[![Pydantic v2](https://img.shields.io/badge/Validation-Pydantic%20v2-E92063.svg?style=flat)](https://docs.pydantic.dev/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-D71F00.svg?style=flat)](https://www.sqlalchemy.org/)
[![Playwright](https://img.shields.io/badge/Browser-Playwright-2EAD33.svg?style=flat&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Rich CLI](https://img.shields.io/badge/UI-Rich%20TUI-cyan.svg?style=flat)](https://github.com/Textualize/rich)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, fault-tolerant, asynchronous web crawling and LLM-powered data intelligence platform. Engineered to autonomously discover, ingest, clean, extract, resolve, validate, and export structured intelligence on the global Artificial Intelligence ecosystem across **Startups, Products, Research Papers, Jobs, and News**.

Built to strictly comply with the requirements of the **GraphOne / FrontierAtlas AI Engineer Assessment Specification**.

---

## 📑 Table of Contents

- [Platform Architecture](#-platform-architecture)
- [Key Features & Specification Adherence](#-key-features--specification-adherence)
- [Quick Start Guide](#-quick-start-guide)
  - [Prerequisites](#prerequisites)
  - [Windows Setup (PowerShell & CMD)](#windows-setup)
  - [Linux / macOS Setup](#linux--macos-setup)
- [Running the Rich Interactive TUI & CLI](#-running-the-rich-interactive-tui--cli)
  - [Interactive Mode](#1-interactive-terminal-ui-tui)
  - [Direct Command-Line Flags](#2-direct-command-line-flags)
- [Headless Pipeline Execution](#-headless-pipeline-execution)
- [6-Tab Data Export Specification](#-6-tab-data-export-specification)
- [Testing & Diagnostics](#-testing--diagnostics)
- [Docker Production Deployment](#-docker-production-deployment)
- [Configuration Reference](#-configuration-reference)
- [Repository File Structure](#-repository-file-structure)
- [Engineering Documentation](#-engineering-documentation)

---

## 🏗️ Platform Architecture

```
                                External Web Sources
              (YC, arXiv, Papers with Code, TechCrunch, Job Boards)
                                       │
                                       ▼
                     [1. Source Discovery & URL Frontier]
            (Sitemaps, RSS, Priority Queue, Canonical Dedup)
                                       │
                                       ▼
                           [2. Adaptive Fetcher]
             ┌─────────────────────────┴────────────────────────┐
             ▼                                                  ▼
     [Tier 1: aiohttp]                               [Tier 2: Playwright]
 (High-speed HTTP Fetching)                      (Headless Browser Escalation)
             └─────────────────────────┬────────────────────────┘
                                       ▼
                       [3. DOM Cleaner & Chunker]
            (Removes scripts, styles, boilerplate; handles HTTP 413)
                                       │
                                       ▼
                      [4. Multi-Provider LLM Chain]
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
     [Gemini 2.0 Flash]        [Groq Llama 3 70B]        [DeepSeek V3 / Mock]
        (Primary)                 (Secondary)             (Tertiary / Offline)
            └──────────────────────────┬──────────────────────────┘
                                       ▼
                        [5. Validation & Intelligence]
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
[Pydantic v2 Schema]          [24h Freshness Filter]         [Entity Resolver]
 (Strict version 1.0)           (0 <= age <= 86400s)         (50 Seed Startups)
       └───────────────────────────────┬───────────────────────────────┘
                                       ▼
                          [6. Deduplication Engine]
                     (Composite SHA-256 Fingerprints)
                                       │
                                       ▼
                       [7. Dual-Mode Storage Layer]
                  (PostgreSQL asyncpg / SQLite aiosqlite)
                                       │
                                       ▼
                       [8. Multi-Tab Export Engine]
         ┌─────────────────────────────┴─────────────────────────────┐
         ▼                                                           ▼
[Google Sheets API]                                          [Local CSV Exports]
  (6 Online Tabs)                                            (data/processed/*.csv)
```

---

## 🌟 Key Features & Specification Adherence

| Spec Requirement | Feature | Implementation Details |
|---|---|---|
| **FR-01 / FR-02** | **Priority URL Frontier** | Thread-safe in-memory and Redis priority queue with task state machine (`PENDING`, `ACTIVE`, `COMPLETED`, `FAILED`). |
| **FR-03** | **Multi-Source Ingestion** | 14+ pre-configured sources across AI Startups, Directories, arXiv, Papers with Code, TechCrunch, VentureBeat, and tech job boards (`configs/sources.yaml`). |
| **FR-04** | **Ethical Rate Limiting** | Token-bucket rate limiter per domain with randomized polite jitter and custom User-Agent headers. |
| **FR-05** | **Adaptive Web Fetching** | Two-tier architecture: High-throughput async HTTP (`aiohttp`) automatically escalates to dynamic headless browser (`Playwright`) upon detecting SPA / JS hydration. |
| **FR-06 / FR-07** | **DOM Sanitization** | Strips scripts, styles, navigation, tracking iframes, and extracts OpenGraph / Twitter / JSON-LD microdata via `selectolax` & `BeautifulSoup4`. |
| **FR-08** | **HTTP 413 Protection** | Semantic sliding-window chunker with token budget management and multi-chunk result merging to eliminate payload truncation. |
| **FR-09** | **Strict Pydantic Validation** | Versioned schemas (`1.0`) enforcing required fields, metadata wrappers, and extraction confidence scoring. |
| **FR-10** | **Multi-Provider LLM Fallback** | Automatic fallback chain: **Gemini 2.0 Flash** ➔ **Groq Llama 3 70B** ➔ **DeepSeek V3** ➔ **Deterministic Heuristic Mock**. |
| **FR-11** | **HTTP 429 Resilience** | Exponential backoff with randomized jitter and per-provider circuit breaking. |
| **FR-12** | **Deterministic Entity Resolution** | Canonicalizes company names (e.g. `OpenAI Inc.`, `Open AI`, `OpenAI, Inc.` ➔ `OpenAI`) using a 50-startup seed database, corporate suffix stripping, and audit logging. |
| **FR-13** | **Strict 24h Freshness Filter** | Multi-format date detector (ISO-8601, RFC 2822, relative strings like *"2 hours ago"*). Rejects news and jobs where `age_seconds > 86400`. |
| **FR-14** | **Content Deduplication** | Deterministic SHA-256 composite fingerprinting prevents storing or exporting redundant records. |
| **FR-15** | **Dual-Mode Persistence** | Async SQLAlchemy repository pattern supporting production **PostgreSQL** (`asyncpg`) and zero-dependency local **SQLite** (`aiosqlite`). |
| **FR-16** | **GitHub Metric Correlation** | Asynchronously queries GitHub API to enrich AI research papers with live star counts and repository metadata. |
| **FR-17** | **6-Tab Export Mechanism** | Formats and exports data across all 6 required tabs via Google Sheets API with automatic fallback to local CSV files. |
| **NFR-07** | **Structured JSON Logging** | Production-ready structured JSON logging with timestamps, source context, task IDs, and log levels. |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.12+**
- Git
- *(Optional)* Google Gemini, Groq, or DeepSeek API key (Mock fallback operates seamlessly offline without keys)

---

### Windows Setup

#### 1. Clone the repository & enter the folder
```powershell
git clone https://github.com/your-org/intelligent-web-scraper.git
cd E:\IntelligentWebCrawler
```

#### 2. Create and Activate Virtual Environment
```powershell
# Create venv
python -m venv .venv

# Activate venv in PowerShell:
.\.venv\Scripts\Activate.ps1

# Or in Command Prompt (CMD):
.\.venv\Scripts\activate.bat
```

#### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

#### 4. Configure Environment
```powershell
copy .env.example .env
```
*(Optionally add your `GEMINI_API_KEY`, `GROQ_API_KEY`, or `DATABASE_URL` in `.env`).*

#### 5. Initialize Database & Seed 50 AI Startups
```powershell
python scripts/initialize_db.py
```

---

### Linux / macOS Setup

```bash
git clone https://github.com/your-org/intelligent-web-scraper.git
cd intelligent-web-scraper

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
cp .env.example .env
python scripts/initialize_db.py
```

---

## 💻 Running the Rich Interactive TUI & CLI

The platform includes an interactive, rich terminal application featuring styled ASCII banners, live progress bars, spinners, and data viewers.

### 1. Interactive Terminal UI (TUI)

Inside `E:\IntelligentWebCrawler`:

```powershell
# In PowerShell (always prefix with .\):
.\run.ps1

# In Command Prompt (CMD):
run.bat

# Or directly with Python:
python cli.py
```

#### Interactive Menu Options:
```
╔═════════════════════════════════════════════════════════════════════════════╗
║           Intelligent Web Scraping & AI-Powered Data Intelligence           ║
║             GraphOne / FrontierAtlas - AI Engineer Assessment               ║
╚═════════════════════════════════════════════════════════════════════════════╝
┌── Platform Navigation Menu ─────────────────────────────────────────────────┐
│  [1]  🚀 Run Crawler & Extraction Pipeline                                  │
│  [2]  🔍 Discover Candidate URLs from Web Sources                           │
│  [3]  🏢 Entity Resolution Explorer (Live Alias Lookup)                     │
│  [4]  📊 Inspect Data Records (6 Tabs / Processed CSVs)                     │
│  [5]  📁 Export Data (Google Sheets & Local CSVs)                           │
│  [6]  ⚙️ Database & Seed Management (50 AI Startups)                        │
│  [7]  🧪 Run Platform Diagnostics & Test Suites                             │
│  [0]  🚪 Exit Platform                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Direct Command-Line Flags

You can bypass the interactive menu by passing direct CLI flags:

| Command | Action |
|---|---|
| `.\run.bat --run --max-tasks 10` | Run discovery, scraping, LLM extraction, and 6-tab export |
| `.\run.bat --discover` | Scrapes configured sources and prints a Rich table of discovered URLs |
| `.\run.bat --resolve "Open AI Inc"` | Test canonical entity resolution and display result panel |
| `.\run.bat --view A` | View row counts and file paths across all 6 processed tabs |
| `.\run.bat --view 2` | Inspect records from Tab 2 (*Products*) in a formatted table |
| `.\run.bat --stats` | View database record counts and storage engine metrics |
| `.\run.bat --export` | Trigger immediate 6-tab export to Google Sheets / CSV |
| `.\run.bat --test` | Run the diagnostic test suite with Rich formatting |

---

## ⚡ Headless Pipeline Execution

To run the platform as a background worker or cron job:

```bash
# Ingestion pipeline in headless mode (default: 50 tasks)
python src/intelligent_scraper/main.py --mode run --max-tasks 20

# Run in discovery mode only
python src/intelligent_scraper/main.py --mode discover

# Run export only
python src/intelligent_scraper/main.py --mode export

# Enable structured JSON logs (NFR-07)
python src/intelligent_scraper/main.py --mode run --json-logs
```

---

## 📊 6-Tab Data Export Specification

The platform exports all extracted intelligence across **6 distinct tabs** (Google Sheets API or CSV fallback in `data/processed/`):

| Tab # | Tab Name | Local File | Schema Fields |
|---|---|---|---|
| **Tab 1** | **Startups** | `startups.csv` | `Schema Version`, `Record Type`, `Source Name`, `Source URL`, `Startup Name`, `Employee Count`, `Collected At` |
| **Tab 2** | **Products** | `products.csv` | `Schema Version`, `Record Type`, `Source Name`, `Source URL`, `Startup Name`, `Product Name`, `Pricing Model`, `Collected At` |
| **Tab 3** | **Research Papers** | `research_papers.csv` | `Schema Version`, `Record Type`, `Source Name`, `Source URL`, `Title`, `Authors`, `Paper URL`, `GitHub URL`, `GitHub Stars`, `Published Date`, `Collected At` |
| **Tab 4** | **Jobs** | `jobs.csv` | `Schema Version`, `Record Type`, `Source Name`, `Source URL`, `Company`, `Role Title`, `Role Family`, `Is Remote`, `Job URL`, `Published Date`, `Is Fresh (24h)`, `Collected At` |
| **Tab 5** | **News** | `news.csv` | `Schema Version`, `Record Type`, `Source Name`, `Source URL`, `Title`, `Article URL`, `Summary`, `Published Date`, `Is Fresh (24h)`, `Collected At` |
| **Tab 6** | **Entity Mapping Log** | `entity_mapping_log.csv` | `Raw Name`, `Canonical Name`, `Matching Method` (Audit Trail) |

> **Freshness Policy**: Tabs 4 and 5 strictly enforce the 24-hour freshness rule. Unverifiable or stale articles/jobs (`age > 86400s`) are dropped from export.

---

## 🧪 Testing & Diagnostics

The project features a 100% passing test suite covering unit logic, integration pipelines, and end-to-end execution:

### 1. Run Automated Pytest Suite
```powershell
python -m pytest tests/
# Result: 16 passed in 7.15s (100% PASS)
```

### 2. Run Comprehensive Diagnostics Runner
```powershell
python run_tests.py
# Result: 30 PASSED, 0 FAILED (100% PASS)
```

Test Coverage Breakdown:
- **Date Detector & Freshness Validator**: ISO-8601, RFC 2822, relative strings, 24h boundary checks.
- **Deterministic Entity Resolution**: OpenAI variations, corporate suffixes, alias dictionary lookup.
- **HTML Parser & Content Cleaner**: Noise removal, text extraction, link discovery.
- **URL Frontier & Deduplication**: Priority ordering, duplicate prevention.
- **Content Chunker**: Sliding-window chunking, token budgets, result merging.
- **Storage Repositories**: Async SQLAlchemy persistence, record queries.
- **End-to-End Pipeline**: Ingestion, mock LLM extraction, and 6-tab CSV/Sheets export.

---

## 🐳 Docker Production Deployment

Run PostgreSQL, Redis, and the Intelligent Scraper containerized:

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View crawler logs
docker-compose logs -f scraper
```

The `docker-compose.yml` orchestrates:
- **`postgres`**: PostgreSQL 16 database storing entities, tasks, and raw documents.
- **`redis`**: Redis 7 cache for distributed URL Frontier scheduling.
- **`scraper`**: Asynchronous Python crawler with automated migrations and execution.

---

## ⚙️ Configuration Reference

Configuration is managed via environment variables and `.env`:

```ini
# Application Mode
APP_ENV=development
LOG_LEVEL=INFO

# Storage Engines (Postgres / SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/scraper.db
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intelligent_scraper
REDIS_URL=redis://localhost:6379/0

# LLM Providers
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Google Sheets API (Optional)
GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here

# Crawler Politeness & Performance
CRAWLER_CONCURRENCY=5
REQUEST_TIMEOUT_SECONDS=30
RATE_LIMIT_DELAY=1.0
FRESHNESS_WINDOW_SECONDS=86400
```

---

## 📁 Repository File Structure

```
E:\IntelligentWebCrawler
├── configs/                          # Declarative configuration files
│   ├── sources.yaml                  # 14+ registered web crawl sources
│   └── extraction_rules.yaml         # CSS/XPath and schema extraction rules
├── data/
│   ├── processed/                    # Generated 6-tab CSV datasets
│   │   ├── startups.csv
│   │   ├── products.csv
│   │   ├── research_papers.csv
│   │   ├── jobs.csv
│   │   ├── news.csv
│   │   └── entity_mapping_log.csv
│   ├── seed/
│   │   └── ai_startups_seed.json     # 50 Canonical AI startups & aliases
│   └── scraper.db                    # Local SQLite database
├── docs/                             # Engineering specifications & designs
│   ├── SRS.md                        # Software Requirements Specification
│   ├── HLD.md                        # High-Level Architecture Design
│   ├── LLD.md                        # Low-Level Component Design
│   └── IMPLEMENTATION.md             # Scalability & Implementation Guide
├── scripts/                          # Operational CLI scripts
│   ├── initialize_db.py              # DB schema migration & startup seeding
│   ├── run_crawler.py                # Standalone crawler runner
│   └── export_data.py                # Direct database-to-sheets/CSV export
├── src/intelligent_scraper/          # Core platform source code
│   ├── cli.py                        # Rich interactive TUI dashboard & CLI
│   ├── config/                       # Settings & structured JSON logging
│   ├── core/                         # Constants, Enums, Interfaces, Exceptions
│   ├── crawler/                      # aiohttp, Playwright, rate limiter, adaptive fetcher
│   ├── discovery/                    # URL Frontier, priority scheduling, source discovery
│   ├── exporters/                    # 6-tab Google Sheets & local CSV exporter
│   ├── extraction/                   # HTML parser, cleaner, chunker, metadata extractor
│   ├── integrations/                 # GitHub API & Google Sheets API clients
│   ├── intelligence/                 # Date detector, 24h freshness, entity resolver, dedup
│   ├── llm/                          # Gemini, Groq, DeepSeek providers & model router
│   ├── orchestration/                # Pipeline, task manager, retry manager
│   ├── schemas/                      # Pydantic v2 data models
│   ├── storage/                      # SQLAlchemy models & repositories
│   └── main.py                       # Headless CLI entrypoint
├── tests/                            # Automated test suites
│   ├── unit/                         # Unit tests (fetcher, parser, dates, resolver, frontier)
│   ├── integration/                  # Integration tests (crawler, db, llm)
│   └── e2e/                          # End-to-end pipeline execution test
├── cli.py                            # Root CLI entrypoint
├── run.bat                           # 1-Click Windows Command Prompt launcher
├── run.ps1                           # 1-Click Windows PowerShell launcher
├── run_tests.py                      # Standalone 30-item test runner
├── Dockerfile                        # Multi-stage production container
├── docker-compose.yml                # Microservices orchestration
├── requirements.txt                  # Python dependencies
└── pyproject.toml                    # Package build & pytest configuration
```

---

## 📖 Engineering Documentation

Comprehensive architectural and engineering documentation is available in the [`docs/`](file:///e:/IntelligentWebCrawler/docs/) directory:

- 📋 [**SRS.md**](file:///e:/IntelligentWebCrawler/docs/SRS.md): Complete Software Requirements Specification detailing functional requirements FR-01 through FR-17 and non-functional requirements NFR-01 through NFR-10.
- 🏛️ [**HLD.md**](file:///e:/IntelligentWebCrawler/docs/HLD.md): High-Level Design document containing component interaction diagrams, data pipelines, and system topology.
- 📐 [**LLD.md**](file:///e:/IntelligentWebCrawler/docs/LLD.md): Low-Level Design document specifying class interfaces, state machines, sequence diagrams, and error handling protocols.
- 🛠️ [**IMPLEMENTATION.md**](file:///e:/IntelligentWebCrawler/docs/IMPLEMENTATION.md): Technical implementation report covering architectural patterns, performance benchmarks, and scalability considerations.
