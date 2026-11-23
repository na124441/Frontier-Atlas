# High-Level Design (HLD)

## Intelligent Web Scraping & AI-Powered Data Intelligence Platform

### 1. Architectural Overview
The platform implements an asynchronous, modular data intelligence pipeline divided into eight primary layers:

```
External Data Sources
        │
        ▼
[Source Discovery Engine]
        │
        ▼
[URL Frontier & Scheduler]
        │
        ▼
[Adaptive Web Crawler] ──► (HTTP Fetcher / Playwright Browser)
        │
        ▼
[Content Cleaning & Parsing]
        │
        ▼
[LLM Orchestration Engine] ──► (Gemini Flash ──► Groq Llama ──► DeepSeek)
        │
        ▼
[Data Validation & Freshness Filtering (24h)]
        │
        ▼
[Deterministic Entity Resolution & Deduplication]
        │
        ▼
[Persistence Layer (PostgreSQL / SQLite)]
        │
        ▼
[Google Sheets Export (6 Tabs) / CSV Reports]
```

### 2. Core Subsystems

#### 2.1 Source Discovery Layer
- Discovers URLs from registered source configs via sitemaps, feeds, and directory links.
- Respects rate limits, domain boundaries, and robots policies.

#### 2.2 Adaptive Crawling Layer
- **HTTP Fetcher (`aiohttp`)**: Fast, lightweight fetching for static pages and REST APIs.
- **Browser Automation (`Playwright`)**: Headless browser rendering for single-page apps (SPAs) and dynamic JavaScript pages.
- **Adaptive Strategy**: Automatically inspects HTML text density and `<noscript>`/hydration markers to trigger Playwright only when necessary.

#### 2.3 LLM Orchestration & Fallback Chain
- **Primary**: Google Gemini Flash (high throughput, structured JSON).
- **Secondary**: Groq-hosted Llama 3 (ultra-low latency fallback).
- **Tertiary**: DeepSeek.
- **Fallback**: Heuristic Mock extractor for offline execution and testing.
- **Payload Management**: Semantic chunking resolves HTTP 413; exponential backoff with jitter resolves HTTP 429.

#### 2.4 Intelligence & Normalization Layer
- **Date Detector**: Normalizes relative and structured timestamps to UTC ISO-8601.
- **Freshness Filter**: Rejects news/jobs older than 24 hours.
- **Entity Resolver**: Normalizes entity variations to canonical representations using a 50-startup seed database.
- **Deduplicator**: Generates composite fingerprints ensuring duplicate prevention across distributed workers.

#### 2.5 Persistence & Export Layer
- Stores normalized records in relational tables (`startups`, `products`, `research_papers`, `jobs`, `news`).
- Archives raw text and metadata in `raw_documents` for provenance.
- Generates 6-tab outputs for Google Sheets and local CSVs.
