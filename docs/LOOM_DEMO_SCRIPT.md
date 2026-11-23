# Loom Video Demo Script & Walkthrough Guide
## Intelligent Web Scraping & AI-Powered Data Intelligence Platform
**Project**: GraphOne / FrontierAtlas - AI Engineer Assessment  
**Recommended Video Duration**: 3 – 5 Minutes  
**Target Audience**: Technical Evaluators / Hiring Team  

---

## 🎬 Pre-Recording Checklist
Before starting your Loom recording:
1. Open your terminal at `E:\IntelligentWebCrawler`.
2. Ensure your terminal window is readable (font size 14-16, full width).
3. Have your code editor (VS Code / IDE) open side-by-side with the project files.
4. Have the `data/processed/` folder open in your file explorer or code editor.

---

## ⏱️ Timeline & Narration Script

### 📍 [0:00 – 0:45] Introduction & System Overview
- **What to show on screen**: Open [README.md](file:///e:/IntelligentWebCrawler/README.md) or [HLD.md](file:///e:/IntelligentWebCrawler/docs/HLD.md) showing the Architecture Flowchart.
- **What to say**:
  > *"Hi everyone! Welcome to my walkthrough of the Intelligent Web Scraping & AI-Powered Data Intelligence Platform built for the FrontierAtlas assessment. This platform is an enterprise-grade, asynchronous, fault-tolerant crawling and intelligence system designed to discover, extract, validate, deduplicate, and export high-value data on the global AI ecosystem across five core entities: Startups, Products, Research Papers, Jobs, and News.*
  >
  > *The system is architected with a two-tier adaptive fetching engine (aiohttp with automatic Playwright browser escalation), an automatic multi-provider LLM fallback chain, deterministic entity resolution with a 50-startup seed database, strict 24-hour freshness enforcement, and a 6-tab export mechanism for Google Sheets and CSV."*

---

### 📍 [0:45 – 1:45] The Rich Interactive Terminal Dashboard (TUI)
- **What to show on screen**: Open PowerShell or Command Prompt and run:
  ```powershell
  .\run.ps1
  # or
  run.bat
  ```
- **What to say**:
  > *"To provide a world-class operator experience, I built an interactive Rich-based Terminal User Interface (TUI). When we launch the app, you immediately see the system status bar: our storage engine (SQLite with Postgres support), the active LLM fallback chain (Gemini Flash -> Groq Llama 3 -> DeepSeek -> Mock), the strict 24-hour freshness policy, and the platform navigation menu.*
  >
  > *From here, an engineer can run the end-to-end pipeline, discover live URLs, test entity resolution, inspect collected records across all 6 tabs, manage database seeding, and run system diagnostics."*

---

### 📍 [1:45 – 2:45] Live Web Source Discovery & Pipeline Execution
- **What to show on screen**: Select `[1]` in the interactive menu or run in a terminal:
  ```cmd
  run.bat --run --max-tasks 3
  ```
- **What to say**:
  > *"Let's run the ingestion pipeline. As you can see, the platform first initiates Phase 1: Source Discovery. It queries 14+ registered sources across YC, arXiv, Papers with Code, TechCrunch, VentureBeat, and tech job boards, populating our prioritized URL frontier.*
  >
  > *In Phase 2, our adaptive crawler ingests each page. It uses aiohttp for high-speed retrieval, but automatically escalates to a headless Playwright browser if client-side JavaScript rendering or dynamic hydration is detected. The content is sanitized, chunked to respect token budgets and prevent HTTP 413 payload errors, and processed through our LLM extraction router.*
  >
  > *Notice the live execution summary: candidate URLs discovered, tasks processed, and successful extractions."*

---

### 📍 [2:45 – 3:30] Deterministic Entity Resolution & 24h Freshness
- **What to show on screen**: Run:
  ```cmd
  run.bat --resolve "Open AI Inc"
  run.bat --resolve "Anthropic PBC"
  run.bat --resolve "Mistral AI SAS"
  ```
- **What to say**:
  > *"A critical requirement of the assessment is Deterministic Entity Resolution (FR-12). Raw web data contains noisy corporate names like 'Open AI Inc.', 'OpenAI, Inc.', and 'OpenAI LLC'.*
  >
  > *Our resolution engine normalizes the input, strips corporate suffixes, performs compact alphanumeric hashing, and references our 50 canonical AI startups seed database to deterministically map them to 'OpenAI'. Every mapping is recorded in our audit trail.*
  >
  > *Simultaneously, for time-sensitive entities like Jobs and News, our Freshness Validator strictly rejects any record older than 24 hours (86,400 seconds), ensuring only fresh intelligence enters the platform."*

---

### 📍 [3:30 – 4:15] Six-Tab Data Export & Persistence
- **What to show on screen**: Run:
  ```cmd
  run.bat --view A
  ```
  Open `data/processed/products.csv` and `data/processed/entity_mapping_log.csv` to show real extracted rows.
- **What to say**:
  > *"All collected intelligence is persisted using async SQLAlchemy and exported across the six required tabs: Startups, Products, Research Papers, Jobs, News, and the Entity Mapping Log.*
  >
  > *If Google Sheets credentials are configured, it syncs directly to the online spreadsheet via the Google Sheets API with cell batching and rate-limit backoff. When running offline or locally, it generates clean, standardized CSV files in data/processed/. Notice that each record includes our Schema Version 1.0, provenance URLs, and confidence scores."*

---

### 📍 [4:15 – 5:00] Test Suite Verification & Conclusion
- **What to show on screen**: Run:
  ```cmd
  python run_tests.py
  # and optionally:
  python -m pytest tests/
  ```
- **What to say**:
  > *"Finally, system integrity and reliability are backed by a comprehensive automated test suite. Running our test diagnostics, we have 30 out of 30 tests passing with 0 failures across date detection, entity resolution, HTML sanitization, URL frontier scheduling, content chunking, database repositories, and end-to-end pipeline execution.*
  >
  > *The platform is fully containerized with Docker Compose for production deployment with PostgreSQL and Redis.*
  >
  > *Thank you for your time, and I look forward to discussing the platform further!"*

---

## 💡 Key Architectural Buzzwords to Emphasize
- **Fault-Tolerant & Adaptive**: Two-tier `aiohttp` + `Playwright` escalation.
- **Multi-Provider Fallback**: Gemini 2.0 Flash ➔ Groq Llama 3 ➔ DeepSeek V3 ➔ Mock.
- **HTTP 413 / 429 Protection**: Sliding-window chunking & exponential backoff with jitter.
- **Deterministic Resolution**: 50 Canonical AI Startups Seed + audit mapping logs.
- **Freshness Window**: Strict 24-hour enforcement (`0 <= age <= 86400s`).
- **Composite Deduplication**: SHA-256 fingerprinting.
