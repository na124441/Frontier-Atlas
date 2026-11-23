"""Unit tests for Entity Resolver."""
import pytest
from intelligent_scraper.intelligence.entity_resolver import EntityResolver


def test_entity_resolution_known_canonical():
    resolver = EntityResolver()

    # Exact variations specified in SRS FR-12
    assert resolver.resolve_entity("OpenAI") == "OpenAI"
    assert resolver.resolve_entity("Open AI") == "OpenAI"
    assert resolver.resolve_entity("OpenAI Inc.") == "OpenAI"
    assert resolver.resolve_entity("OpenAI, Inc.") == "OpenAI"
    assert resolver.resolve_entity("OpenAI LLC") == "OpenAI"

    # Anthropic
    assert resolver.resolve_entity("Anthropic PBC") == "Anthropic"
    assert resolver.resolve_entity("Anthropic AI") == "Anthropic"

    # Perplexity
    assert resolver.resolve_entity("Perplexity AI Inc") == "Perplexity AI"


def test_entity_resolver_mapping_logs():
    resolver = EntityResolver()
    resolver.resolve_entity("OpenAI Inc.")
    resolver.resolve_entity("Mistral AI SAS")

    logs = resolver.get_mapping_logs()
    assert len(logs) >= 2
    raw_names = [l["raw_name"] for l in logs]
    assert "OpenAI Inc." in raw_names
