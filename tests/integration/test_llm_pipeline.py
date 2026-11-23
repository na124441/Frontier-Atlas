"""Integration tests for LLM Extraction and Fallback Chain."""
import pytest
from intelligent_scraper.core.enums import RecordType
from intelligent_scraper.llm.model_router import ModelRouter
from intelligent_scraper.llm.extraction_service import ExtractionService
from intelligent_scraper.extraction.content_chunker import ContentChunker


@pytest.mark.asyncio
async def test_llm_extraction_service_with_mock():
    service = ExtractionService()
    content = "OpenAI is an AI research company with 1200 employees developing ChatGPT."
    result = await service.extract_entity(
        content=content,
        record_type=RecordType.STARTUP,
        source_url="https://openai.com"
    )

    assert "entityName" in result
    assert result["entityName"] in ("OpenAI", "Extracted AI")


@pytest.mark.asyncio
async def test_chunker_merging():
    chunker = ContentChunker(max_tokens=50)
    text = (
        "Section 1: OpenAI introduced new safety evaluations for artificial general intelligence. "
        "The system has been trained on multiple diverse datasets.\n\n"
        "Section 2: The company employs 1200 people across San Francisco and London offices."
    )
    chunks = chunker.create_chunks(text)
    assert len(chunks) >= 2

    partial_res1 = {"entityName": "OpenAI", "employeeCount": None}
    partial_res2 = {"entityName": "OpenAI", "employeeCount": 1200}
    merged = chunker.merge_chunk_results([partial_res1, partial_res2])

    assert merged["entityName"] == "OpenAI"
    assert merged["employeeCount"] == 1200
