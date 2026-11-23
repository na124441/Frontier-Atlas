"""Unit tests for Adaptive Fetcher."""
import pytest
from intelligent_scraper.crawler.adaptive_fetcher import AdaptiveFetcher


def test_requires_browser_rendering_heuristics():
    fetcher = AdaptiveFetcher()

    # Plain static page
    static_html = "<html><body><h1>OpenAI Announces GPT-5</h1><p>Full article text here with sufficient content.</p></body></html>"
    assert not fetcher.requires_browser_rendering(static_html)

    # Empty SPA root div
    spa_html = "<html><body><div id='root'></div><script src='/bundle.js'></script></body></html>"
    assert fetcher.requires_browser_rendering(spa_html)

    # Explicit noscript tag
    noscript_html = "<html><body><noscript>Please enable JavaScript to view this application.</noscript></body></html>"
    assert fetcher.requires_browser_rendering(noscript_html)

    # Source config explicitly requesting browser
    assert fetcher.requires_browser_rendering(static_html, source_config={"strategy": "browser"})
