# Low-Level Design (LLD)

## Module Specifications & Class Contracts

### 1. Module Hierarchy
```
intelligent-web-scraper/
├── src/intelligent_scraper/
│   ├── config/ (settings.py, logging_config.py)
│   ├── core/ (enums.py, exceptions.py, constants.py, interfaces.py)
│   ├── discovery/ (source_registry.py, source_discovery.py, sitemap_parser.py, url_frontier.py)
│   ├── crawler/ (rate_limiter.py, http_fetcher.py, browser_engine.py, adaptive_fetcher.py, async_crawler.py)
│   ├── extraction/ (html_parser.py, content_cleaner.py, metadata_extractor.py, content_chunker.py)
│   ├── llm/ (base_provider.py, gemini_provider.py, groq_provider.py, deepseek_provider.py, model_router.py, extraction_service.py)
│   ├── intelligence/ (date_detector.py, freshness_validator.py, entity_resolver.py, deduplicator.py, confidence_validator.py)
│   ├── schemas/ (base.py, startup.py, product.py, research_paper.py, job.py, news.py)
│   ├── orchestration/ (retry_manager.py, task_manager.py, pipeline.py)
│   ├── storage/ (database.py, models/, repositories/)
│   ├── integrations/ (github_client.py, google_sheets_client.py)
│   ├── exporters/ (sheets_exporter.py)
│   └── main.py
```

### 2. Key Class Contracts

#### 2.1 ExtractionService (`llm/extraction_service.py`)
- `extract_entity(content: str, record_type: RecordType, source_url: str) -> Dict[str, Any]`
- Evaluates token estimate with `ContentChunker`.
- If payload exceeds limit, breaks text into semantic chunks and merges structured outputs.

#### 2.2 ModelRouter (`llm/model_router.py`)
- `execute_request(prompt: str, content: str, schema: Type[BaseModel]) -> Dict[str, Any]`
- Orchestrates primary (Gemini Flash), secondary (Groq), and tertiary (DeepSeek).
- Calculates backoff delay: `delay = min(max_delay, base_delay * (2 ^ retry_count)) + random_jitter`.

#### 2.3 DateDetector & FreshnessValidator (`intelligence/`)
- Normalizes ISO-8601, epoch timestamps, and strings like "2 hours ago".
- Formula: `0 <= (reference_time - published_at).total_seconds() <= 86400`.

#### 2.4 EntityResolver (`intelligence/entity_resolver.py`)
- Strips legal suffixes (Inc., LLC, Ltd, Corp, AI).
- Queries canonical seed index.
- Logs mappings into `entity_mappings` for Tab 6 export.

#### 2.5 Deduplicator (`intelligence/deduplicator.py`)
- Computes SHA-256 composite fingerprint per entity type:
  - Startup: `startup:{canonical_name}`
  - Product: `product:{startup}:{product_name}`
  - Paper: `paper:arxiv:{arxiv_id}` or canonical URL
  - Job: `job:{company}:{role}:{url}`
  - News: `news:{canonical_article_url}`
