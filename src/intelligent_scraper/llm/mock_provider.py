"""
Mock / Rule-Based Offline Provider for local development, tests, and offline execution.
Ensures zero-friction development without requiring active API keys.
"""

import re
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from intelligent_scraper.llm.base_provider import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    """Fallback provider when external LLM API credentials are not set."""

    def __init__(self, name: str = "mock", model_name: str = "heuristic-mock", api_key: str = "mock"):
        super().__init__(name=name, model_name=model_name, api_key=api_key)

    async def health_check(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        content: str,
        schema: Optional[Type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """Synthesizes structured schema response using deterministic heuristic parsing."""
        schema_name = schema.__name__ if schema else ""

        if "Startup" in schema_name or "entityName" in prompt:
            # Extract first notable capitalization
            name_match = re.search(r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)\b', content)
            entity_name = name_match.group(1) if name_match else "Extracted AI"
            emp_match = re.search(r'(\d+)\s+(?:employees|team members|people)', content, re.I)
            employee_count = int(emp_match.group(1)) if emp_match else 50
            return {
                "entityName": entity_name,
                "employeeCount": employee_count
            }

        elif "Product" in schema_name or "pricingModel" in prompt:
            pricing = "FREEMIUM"
            if re.search(r'\bfree\b', content, re.I):
                pricing = "FREE"
            elif re.search(r'\benterprise\b', content, re.I):
                pricing = "ENTERPRISE"
            elif re.search(r'\bpaid|subscription\b', content, re.I):
                pricing = "PAID"
            name_match = re.search(r'\b([A-Z][a-zA-Z0-9]+)\b', content)
            startup_name = name_match.group(1) if name_match else "AI Tool"
            return {
                "startupName": startup_name,
                "pricingModel": pricing,
                "productName": f"{startup_name} Assistant"
            }

        elif "Research" in schema_name or "authors" in prompt:
            first_line = content.split("\n")[0] if content else "Untitled Paper"
            title = first_line[:120] if len(first_line) > 5 else "Advances in Foundation Models"
            authors_match = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+)', content)
            authors = authors_match[:3] if authors_match else ["J. Doe", "A. Turing"]
            github_match = re.search(r'https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+', content)
            github_url = github_match.group(0) if github_match else None
            return {
                "title": title,
                "authors": authors,
                "paper_url": "https://arxiv.org/abs/2401.00001",
                "github_url": github_url,
                "github_stars": 120 if github_url else None,
                "published_date": "2024-01-01T00:00:00Z"
            }

        elif "Job" in schema_name or "role_family" in prompt:
            company_match = re.search(r'(?:at|company:?)\s+([A-Z][a-zA-Z0-9]+)', content, re.I)
            company = company_match.group(1) if company_match else "AI Labs"
            is_remote = bool(re.search(r'\bremote\b', content, re.I))
            return {
                "company": company,
                "date": "2024-01-01T00:00:00Z",
                "is_remote": is_remote,
                "role_family": "Engineering",
                "title": "Machine Learning Engineer"
            }

        elif "News" in schema_name or "full_text" in prompt:
            first_line = content.split("\n")[0] if content else "AI News Update"
            return {
                "title": first_line[:100],
                "article_url": "https://news.ycombinator.com",
                "full_text": content[:500],
                "published_date": "2024-01-01T00:00:00Z"
            }

        return {"raw_content": content[:200]}
