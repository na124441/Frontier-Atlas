# Implementation Guide & Scalability Path

## 1. Setup & Local Development

### 1.1 Virtual Environment
```bash
# Using python 3.12
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

### 1.2 Database Initialization
```bash
# Initialize SQLite or PostgreSQL schemas and load 50 startup seeds
python scripts/initialize_db.py
```

### 1.3 Running the Crawler
```bash
# Run crawler pipeline for discovery and structured extraction
python src/intelligent_scraper/main.py --mode run --max-tasks 20
```

### 1.4 Exporting Datasets
```bash
# Exports 6 tabs to Google Sheets (if credentials configured) or local CSV files in ./data/processed
python scripts/export_data.py
```

---

## 2. Path to 500,000+ Records (Scalability Architecture)

1. **Decoupled Worker Architecture**:
   - Separate lightweight HTTP Crawlers from Playwright Browser workers and LLM processing workers.
   - Use Redis sorted sets for task prioritization and atomic task claiming (`ZPOPMIN`).

2. **Distributed Persistence**:
   - PostgreSQL table partitioning by month and record type.
   - B-tree indexes on `fingerprint`, `source_id`, `published_date`, and `status`.
   - Batch insert statements (`INSERT ... ON CONFLICT DO NOTHING`) with batch sizes of 500-1,000 records.

3. **LLM Cost & Throughput Optimization**:
   - Multi-tier provider caching: Store exact content hashes to avoid re-invoking LLMs for unchanged pages.
   - Dynamic token budgeting and semantic deduplication prior to calling model APIs.
