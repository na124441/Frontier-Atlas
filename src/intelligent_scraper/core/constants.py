"""
Global constants and headers for Intelligent Web Scraper.
"""

# Default HTTP headers conforming to ethical crawling practices
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (IntelligentDataCrawler/1.0; +https://graphone.internal)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Freshness constant: 24 hours in seconds
FRESHNESS_WINDOW_SECONDS = 86400

# Canonical Entity Seed Startups
SEED_STARTUPS = [
    "OpenAI",
    "Anthropic",
    "Mistral AI",
    "Cohere",
    "Hugging Face",
    "Perplexity AI",
    "Scale AI",
    "Databricks",
    "xAI",
    "Stability AI",
    "ElevenLabs",
    "Runway",
    "Jasper",
    "Midjourney",
    "Together AI",
    "Anyscale",
    "Character.ai",
    "Synthesia",
    "Anysphere",  # Cursor
    "Glean",
    "Adept AI",
    "Inflection AI",
    "Fireworks AI",
    "Writer",
    "Poolside",
    "Harvey",
    "Cognition AI",
    "Sierra",
    "Decagon",
    "Sakana AI",
    "Shield AI",
    "DeepL",
    "Replit",
    "Weights & Biases",
    "Pinecone",
    "Weaviate",
    "Qdrant",
    "Chroma",
    "LangChain",
    "LlamaIndex",
    "Modal",
    "OctoAI",
    "Baseten",
    "Groq",
    "Cerebras",
    "SambaNova",
    "dbt Labs",
    "Tabnine",
    "Cohere Health",
    "Hippocratic AI"
]
