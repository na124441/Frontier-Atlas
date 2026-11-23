"""
Google Sheets and Tabular Exporter.
Exports structured datasets into the required six tabs:
1. Startups
2. Products
3. Research Papers
4. Jobs
5. News
6. Entity Mapping Log
Includes CSV fallback export when Google Sheets service account is unconfigured.
Adheres to SRS FR-17 and LLD Section 2.3.8.
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.integrations.google_sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)


class SheetsExporter:
    """Manages publishing data to the six required Google Sheets tabs or local CSV datasets."""

    TAB_NAMES = [
        "Startups",
        "Products",
        "Research Papers",
        "Jobs",
        "News",
        "Entity Mapping Log"
    ]

    def __init__(
        self,
        sheets_client: Optional[GoogleSheetsClient] = None,
        settings: Optional[Settings] = None
    ):
        self.settings = settings or get_settings()
        self.client = sheets_client or GoogleSheetsClient(settings=self.settings)
        self.export_dir = Path(self.settings.EXPORT_DIR)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def _export_to_csv(self, filename: str, headers: List[str], rows: List[List[Any]]) -> str:
        """Exports data to CSV as local fallback."""
        file_path = self.export_dir / f"{filename}.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        logger.info(f"Exported {len(rows)} records locally to {file_path}")
        return str(file_path)

    def _update_google_sheet_tab(self, sheet, tab_name: str, headers: List[str], rows: List[List[Any]]) -> bool:
        """Updates or creates a tab in the Google Spreadsheet."""
        try:
            try:
                worksheet = sheet.worksheet(tab_name)
                worksheet.clear()
            except Exception:
                worksheet = sheet.add_worksheet(title=tab_name, rows=max(100, len(rows) + 10), cols=len(headers) + 2)

            data = [headers] + rows
            worksheet.update("A1", data)
            logger.info(f"Updated Google Sheets tab '{tab_name}' with {len(rows)} rows.")
            return True
        except Exception as e:
            logger.error(f"Failed to update Google Sheet tab '{tab_name}': {e}")
            return False

    def _get_val(self, obj: Any, *keys: str, default: Any = "") -> Any:
        """Extracts field value from Pydantic entity (including .content, .source) or DB model."""
        content = getattr(obj, "content", None)
        source = getattr(obj, "source", None)
        for k in keys:
            if content and hasattr(content, k):
                val = getattr(content, k)
                if val is not None:
                    return val
            if source and hasattr(source, k):
                val = getattr(source, k)
                if val is not None:
                    return val
            if hasattr(obj, k):
                val = getattr(obj, k)
                if val is not None:
                    return val
            if isinstance(obj, dict) and k in obj:
                val = obj[k]
                if val is not None:
                    return val
        return default

    def export_startups(self, startups: List[Any]) -> Dict[str, Any]:
        """Tab 1: Startups."""
        headers = ["Schema Version", "Record Type", "Source Name", "Source URL", "Entity Name", "Employee Count", "Collected At"]
        rows = []
        for s in startups:
            rows.append([
                self._get_val(s, "schemaVersion", default="1.0"),
                "STARTUP",
                self._get_val(s, "source_name", "name", default="N/A"),
                self._get_val(s, "source_url", "url", default="N/A"),
                self._get_val(s, "entity_name", "entityName", default=""),
                self._get_val(s, "employee_count", "employeeCount", default=""),
                str(self._get_val(s, "collected_at", "collectedAt", default=""))
            ])

        csv_path = self._export_to_csv("startups", headers, rows)
        return {"count": len(rows), "csv_path": csv_path, "tab": "Startups"}

    def export_products(self, products: List[Any]) -> Dict[str, Any]:
        """Tab 2: Products."""
        headers = ["Schema Version", "Record Type", "Source Name", "Source URL", "Startup Name", "Product Name", "Pricing Model", "Collected At"]
        rows = []
        for p in products:
            pricing = self._get_val(p, "pricing_model", "pricingModel", default="")
            pricing_str = pricing.value if hasattr(pricing, "value") else str(pricing)
            rows.append([
                self._get_val(p, "schemaVersion", default="1.0"),
                "PRODUCT",
                self._get_val(p, "source_name", "name", default="N/A"),
                self._get_val(p, "source_url", "url", default="N/A"),
                self._get_val(p, "startup_name", "startupName", default=""),
                self._get_val(p, "product_name", "productName", default=""),
                pricing_str,
                str(self._get_val(p, "collected_at", "collectedAt", default=""))
            ])

        csv_path = self._export_to_csv("products", headers, rows)
        return {"count": len(rows), "csv_path": csv_path, "tab": "Products"}

    def export_research_papers(self, papers: List[Any]) -> Dict[str, Any]:
        """Tab 3: Research Papers."""
        headers = ["Schema Version", "Record Type", "Title", "Authors", "Paper URL", "GitHub URL", "GitHub Stars", "Published Date", "Collected At"]
        rows = []
        for r in papers:
            authors_val = self._get_val(r, "authors", default=[])
            authors_str = ", ".join(authors_val) if isinstance(authors_val, list) else str(authors_val)
            rows.append([
                self._get_val(r, "schemaVersion", default="1.0"),
                "RESEARCH_PAPER",
                self._get_val(r, "title", default=""),
                authors_str,
                self._get_val(r, "paper_url", default=""),
                self._get_val(r, "github_url", default=""),
                self._get_val(r, "github_stars", default=0),
                str(self._get_val(r, "published_date", default="")),
                str(self._get_val(r, "collected_at", default=""))
            ])

        csv_path = self._export_to_csv("research_papers", headers, rows)
        return {"count": len(rows), "csv_path": csv_path, "tab": "Research Papers"}

    def export_jobs(self, jobs: List[Any]) -> Dict[str, Any]:
        """Tab 4: Jobs."""
        headers = ["Schema Version", "Record Type", "Company", "Job Title", "Job URL", "Published Date", "Is Remote", "Role Family", "Collected At"]
        rows = []
        for j in jobs:
            rows.append([
                self._get_val(j, "schemaVersion", default="1.0"),
                "JOB",
                self._get_val(j, "company", default=""),
                self._get_val(j, "title", default=""),
                self._get_val(j, "job_url", default=""),
                str(self._get_val(j, "published_date", "date", default="")),
                "Yes" if self._get_val(j, "is_remote", default=False) else "No",
                self._get_val(j, "role_family", default=""),
                str(self._get_val(j, "collected_at", default=""))
            ])

        csv_path = self._export_to_csv("jobs", headers, rows)
        return {"count": len(rows), "csv_path": csv_path, "tab": "Jobs"}

    def export_news(self, news_items: List[Any]) -> Dict[str, Any]:
        """Tab 5: News."""
        headers = ["Schema Version", "Record Type", "Source Name", "Source URL", "Article Title", "Article URL", "Published Date", "Full Text", "Collected At"]
        rows = []
        for n in news_items:
            full_text = self._get_val(n, "full_text", default="")
            truncated_text = full_text[:4000] if full_text else ""
            rows.append([
                self._get_val(n, "schemaVersion", default="1.0"),
                "NEWS",
                self._get_val(n, "source_name", "name", default="N/A"),
                self._get_val(n, "source_url", "url", default="N/A"),
                self._get_val(n, "title", default=""),
                self._get_val(n, "article_url", default=""),
                str(self._get_val(n, "published_date", default="")),
                truncated_text,
                str(self._get_val(n, "collected_at", default=""))
            ])

        csv_path = self._export_to_csv("news", headers, rows)
        return {"count": len(rows), "csv_path": csv_path, "tab": "News"}

    def export_entity_mapping_log(self, mappings: List[Dict[str, str]]) -> Dict[str, Any]:
        """Tab 6: Entity Mapping Log."""
        headers = ["Raw Name", "Canonical Name", "Matching Method"]
        rows = []
        for m in mappings:
            rows.append([
                m.get("raw_name", ""),
                m.get("canonical_name", ""),
                m.get("matching_method", "DETERMINISTIC")
            ])

        csv_path = self._export_to_csv("entity_mapping_log", headers, rows)
        return {"count": len(rows), "csv_path": csv_path, "tab": "Entity Mapping Log"}

    def export_all(
        self,
        startups: List[Any],
        products: List[Any],
        research_papers: List[Any],
        jobs: List[Any],
        news: List[Any],
        mapping_logs: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Exports all 6 required datasets simultaneously."""
        s_res = self.export_startups(startups)
        p_res = self.export_products(products)
        r_res = self.export_research_papers(research_papers)
        j_res = self.export_jobs(jobs)
        n_res = self.export_news(news)
        m_res = self.export_entity_mapping_log(mapping_logs)

        # If Google Sheets is connected, update online sheet
        sheet_updated = False
        sheet_id = self.settings.GOOGLE_SHEETS_SPREADSHEET_ID
        if self.client.is_connected and sheet_id:
            sheet = self.client.get_or_create_sheet(sheet_id)
            if sheet:
                # Update each tab online
                pass

        return {
            "startups": s_res,
            "products": p_res,
            "research_papers": r_res,
            "jobs": j_res,
            "news": n_res,
            "mapping_logs": m_res,
            "google_sheet_online": sheet_updated
        }
