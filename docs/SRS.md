# Software Requirements Specification (SRS)

## Intelligent Web Scraping & AI-Powered Data Intelligence Platform

**Project**: GraphOne / FrontierAtlas – AI Engineer Assessment  
**Document Version**: 1.0  
**Primary Language**: Python 3.12+  
**Operating Environment**: Linux / Windows, Docker-compatible  

---

### 1. Introduction

#### 1.1 Purpose
The purpose of this SRS is to define the functional and non-functional requirements of an Intelligent Web Scraping and AI-Powered Data Intelligence Platform. The system automates discovery, acquisition, extraction, normalization, validation, and storage of structured intelligence from multiple internet sources, targeting AI startups, products, research papers, repositories, news, and job postings.

#### 1.2 Problem Statement
Traditional scrapers face heterogeneous layouts, client-side JavaScript rendering, anti-bot controls, LLM rate limits/context restrictions (HTTP 429/413), entity variations, relative timestamps, and duplication. This platform delivers a fault-tolerant, asynchronous ingestion architecture.

#### 1.3 Key Objectives & Targets
- Scale to 500,000+ records.
- Minimum initial collection targets:
  - 1,000 Startups
  - 1,000 Products
  - 1,000 Research Papers (with correlated GitHub metrics)
  - 5 AI News sources (24-hour freshness enforced)
  - 5 AI Job boards (24-hour freshness enforced)
- Multi-provider LLM fallback chain: Gemini Flash -> Groq Llama -> DeepSeek.
- Deterministic Entity Resolution with ~50 startup seed database.
- Export to Google Sheets across 6 dedicated tabs.

---

### 2. Functional Requirements

- **FR-01: Intelligent Source Discovery**: Configurable sources (startup directories, product directories, research repositories, GitHub, AI news, job boards). Discovers URLs via sitemaps, RSS feeds, and pagination.
- **FR-02: URL Frontier & Scheduling**: Priority-based scheduling with states `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `RETRY_SCHEDULED`. Prevents duplicate enqueueing.
- **FR-03: Adaptive Web Crawling**: Fast asynchronous HTTP fetching via `aiohttp`; escalates to `Playwright Async` when JavaScript rendering is required.
- **FR-04: Massive Bulk Data Acquisition**: Supports concurrent batch processing capable of ingestion scaling to 500k+ records.
- **FR-05: Research Paper Extraction**: Arxiv and Papers with Code ingestion; extracts titles, authors, paper URLs, and verified GitHub stars.
- **FR-06: News and Job Ingestion**: Monitors 5 news sources and 5 job boards with full-text capture.
- **FR-07: Publication Date Normalization**: Converts dates, meta tags, and relative timestamps ("2 hours ago") to ISO-8601 UTC timestamps.
- **FR-08: Freshness Filtering**: Enforces strict 24-hour freshness window (`0 <= age_seconds <= 86400`).
- **FR-09: LLM-Based Information Extraction**: Structured JSON extraction conforming to Pydantic models.
- **FR-10: Intelligent Content Chunking**: Token estimation and semantic chunking to avoid context limits and recover from HTTP 413.
- **FR-11: Rate Limit Management**: HTTP 429 exponential backoff with randomized jitter and provider fallback.
- **FR-12: Deterministic Entity Resolution**: Canonicalizes variations (e.g., "OpenAI Inc." -> "OpenAI") using normalization rules and seed database.
- **FR-13: Deduplication**: SHA-256 fingerprints across canonical URLs, Arxiv IDs, and entity IDs with database uniqueness constraints.
- **FR-14: Anti-Bot & Restricted Source Handling**: Ethical and compliant crawling using headers, rate limits, APIs, and headless sessions.
- **FR-15: Data Validation**: Required fields, data types, cross-field consistency, and source traceability.
- **FR-16: Data Storage**: Relational and JSON document persistence in PostgreSQL (with SQLite compatibility).
- **FR-17: Google Sheets Export**: Populates 6 tabs: Startups, Products, Research Papers, Jobs, News, Entity Mapping Log.

---

### 3. Non-Functional Requirements
- **NFR-01 Scalability**: Horizontal worker scaling to 500,000+ records.
- **NFR-02 Performance**: Asynchronous non-blocking I/O with semaphore concurrency control.
- **NFR-03 Reliability**: Isolated failure boundaries and idempotent writes.
- **NFR-04 Data Accuracy**: Strictly verifiable data traceable to source URLs.
- **NFR-07 Observability**: Structured JSON logging with task IDs, durations, provider info, and retry states.
