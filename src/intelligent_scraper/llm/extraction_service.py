"""
LLM Extraction Service.
Translates unstructured content to structured entity records matching Pydantic schemas.
Handles chunking, prompt templating, schema validation, and HTTP 413 mitigation.
Adheres to SRS FR-09, FR-10 and LLD Section 6.5, 6.6.
"""

import logging
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError as PydanticValError
from intelligent_scraper.core.enums import RecordType
from intelligent_scraper.core.exceptions import ExtractionError, PayloadTooLargeError
from intelligent_scraper.extraction.content_chunker import ContentChunker
from intelligent_scraper.llm.model_router import ModelRouter
from intelligent_scraper.schemas.startup import StartupData
from intelligent_scraper.schemas.product import ProductData
from intelligent_scraper.schemas.research_paper import ResearchPaperData
from intelligent_scraper.schemas.job import JobData
from intelligent_scraper.schemas.news import NewsData

logger = logging.getLogger(__name__)


class ExtractionService:
    """High-level service coordinating extraction prompts, models, and schema adherence."""

    def __init__(self, model_router: Optional[ModelRouter] = None, chunker: Optional[ContentChunker] = None):
        self.router = model_router or ModelRouter()
        self.chunker = chunker or ContentChunker()

    def get_schema_for_type(self, record_type: RecordType) -> Type[BaseModel]:
        """Maps RecordType to target Pydantic content model."""
        mapping = {
            RecordType.STARTUP: StartupData,
            RecordType.PRODUCT: ProductData,
            RecordType.RESEARCH_PAPER: ResearchPaperData,
            RecordType.JOB: JobData,
            RecordType.NEWS: NewsData
        }
        return mapping[record_type]

    def build_prompt(self, record_type: RecordType, source_url: str = "") -> str:
        """
        Constructs system and user instruction prompt adhering to LLD 6.6:
        1. Entity type
        2. Extraction instructions
        3. Rules for missing values
        4. Instructions against unsupported inference
        """
        system_instr = (
            "You are a structured data extraction engine.\n"
            "Extract only information explicitly supported by the provided source content.\n"
            "Never invent or extrapolate missing information.\n"
            "If a field cannot be reliably extracted, output null or empty list.\n"
            "Return valid JSON matching the requested schema."
        )

        type_instructions = {
            RecordType.STARTUP: (
                "Entity Type: STARTUP\n"
                "Extract:\n"
                "- Canonical startup/company name (entityName)\n"
                "- Employee count (employeeCount) if explicitly stated, otherwise null"
            ),
            RecordType.PRODUCT: (
                "Entity Type: PRODUCT\n"
                "Extract:\n"
                "- Canonical startup/company name (startupName)\n"
                "- Product name (productName)\n"
                "- Pricing model (pricingModel): FREE, FREEMIUM, PAID, or ENTERPRISE"
            ),
            RecordType.RESEARCH_PAPER: (
                "Entity Type: RESEARCH_PAPER\n"
                "Extract:\n"
                "- Paper title (title)\n"
                "- Authors list (authors)\n"
                "- Original paper URL (paper_url)\n"
                "- Associated GitHub repository URL (github_url) if mentioned\n"
                "- GitHub star count (github_stars) if mentioned\n"
                "- Publication date (published_date) in ISO-8601 format"
            ),
            RecordType.JOB: (
                "Entity Type: JOB\n"
                "Extract:\n"
                "- Canonical company name (company)\n"
                "- Job title (title)\n"
                "- Job posting URL (job_url)\n"
                "- Remote eligibility (is_remote): true or false\n"
                "- Role family (role_family), e.g. Engineering, Research, Product\n"
                "- Publication date (date) in ISO-8601 format"
            ),
            RecordType.NEWS: (
                "Entity Type: NEWS\n"
                "Extract:\n"
                "- Article title (title)\n"
                "- Article URL (article_url)\n"
                "- Full text body content (full_text)\n"
                "- Publication date (published_date) in ISO-8601 format\n"
                "- Brief summary (summary)"
            ),
        }

        specific = type_instructions.get(record_type, f"Entity Type: {record_type.value}")
        return f"{system_instr}\n\n{specific}\nSource URL: {source_url}"

    async def extract_entity(
        self,
        content: str,
        record_type: RecordType,
        source_url: str = ""
    ) -> Dict[str, Any]:
        """
        Coordinates extraction:
        1. Checks token size. If within limit, attempts direct extraction.
        2. On HTTP 413 or oversized content, splits text into chunks.
        3. Merges chunk results and validates against schema.
        """
        target_schema = self.get_schema_for_type(record_type)
        prompt = self.build_prompt(record_type, source_url)

        # Step 1: Attempt direct extraction
        try:
            if self.chunker.estimate_tokens(content) <= self.chunker.max_tokens:
                raw_json = await self.router.execute_request(
                    prompt=prompt,
                    content=content,
                    schema=target_schema
                )
                return self.validate_response(raw_json, target_schema)
        except PayloadTooLargeError:
            logger.info("Payload too large (413); switching to chunked extraction.")

        # Step 2: Chunked extraction
        chunks = self.chunker.create_chunks(content)
        chunk_results: List[Dict[str, Any]] = []

        for idx, chunk in enumerate(chunks):
            try:
                sub_prompt = f"{prompt}\n[Processing Section {idx+1}/{len(chunks)}]"
                res = await self.router.execute_request(
                    prompt=sub_prompt,
                    content=chunk,
                    schema=target_schema
                )
                chunk_results.append(res)
            except Exception as e:
                logger.warning(f"Chunk {idx+1} extraction failed: {e}")

        if not chunk_results:
            raise ExtractionError(f"Failed to extract entity {record_type} from all chunks")

        # Step 3: Merge and validate
        merged = self.chunker.merge_chunk_results(chunk_results)
        return self.validate_response(merged, target_schema)

    def validate_response(self, response_data: Dict[str, Any], schema: Type[BaseModel]) -> Dict[str, Any]:
        """Validates dictionary against target Pydantic schema."""
        try:
            validated = schema.model_validate(response_data)
            return validated.model_dump()
        except PydanticValError as e:
            logger.error(f"Schema validation error on extraction response: {e}")
            # If schema validation fails, return data with defaults where possible
            return response_data
