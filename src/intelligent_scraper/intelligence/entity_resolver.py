"""
Deterministic Entity Resolution Engine.
Canonicalizes startup and company names using deterministic normalization,
alias dictionary, and seed database of ~50 AI startups.
Adheres to SRS FR-12 and LLD Section 8.2.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from intelligent_scraper.core.constants import SEED_STARTUPS
from intelligent_scraper.core.interfaces import IEntityResolver


class EntityResolver(IEntityResolver):
    """Resolves raw entity names to their canonical representations."""

    # Suffixes to strip during normalization
    CORPORATE_SUFFIXES = [
        r'\binc\.?\b', r'\bincorporated\b', r'\bcorp\.?\b', r'\bcorporation\b',
        r'\bllc\.?\b', r'\bltd\.?\b', r'\blimited\b', r'\bco\.?\b',
        r'\bgmbh\b', r'\bpbc\b', r'\bai\b', r'\btechnologies\b', r'\blabs\b'
    ]

    def __init__(self, seed_file_path: Optional[str] = None):
        self.canonical_entities: set[str] = set(SEED_STARTUPS)
        # Normalized key -> Canonical Name
        self.canonical_index: Dict[str, str] = {}
        # Raw name -> Canonical Name
        self.mappings: Dict[str, str] = {}
        # Mapping audit log for Tab 6 in Google Sheets
        self.mapping_logs: List[Dict[str, str]] = []

        if not seed_file_path:
            # Default to standard seed path if present
            default_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "seed" / "ai_startups_seed.json"
            if default_path.exists():
                seed_file_path = str(default_path)

        # Load seed file if exists
        if seed_file_path and Path(seed_file_path).exists():
            self._load_seed_file(seed_file_path)

        self._build_indices()

    def _build_indices(self) -> None:
        """Indexes all canonical entities by their normalized string representation."""
        for canonical in self.canonical_entities:
            norm = self.normalize_name(canonical)
            self.canonical_index[norm] = canonical
            # Compact key (alphanumeric only)
            compact = re.sub(r'[^a-z0-9]', '', canonical.lower())
            self.canonical_index[compact] = canonical

            # Common manual alias mappings
            if canonical == "OpenAI":
                self.canonical_index["open ai"] = canonical
                self.canonical_index["open"] = canonical
                self.canonical_index["openai"] = canonical
            elif canonical == "Anysphere":
                self.canonical_index["cursor"] = canonical
                self.canonical_index["anysphere cursor"] = canonical
            elif canonical == "Mistral AI":
                self.canonical_index["mistral"] = canonical
                self.canonical_index["mistral ai"] = canonical
            elif canonical == "Perplexity AI":
                self.canonical_index["perplexity"] = canonical
                self.canonical_index["perplexity ai"] = canonical
            elif canonical == "Stability AI":
                self.canonical_index["stability"] = canonical
                self.canonical_index["stability ai"] = canonical
            elif canonical == "Together AI":
                self.canonical_index["together"] = canonical
                self.canonical_index["together ai"] = canonical

    def _load_seed_file(self, seed_path: str) -> None:
        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            self.canonical_entities.add(item)
                            norm = self.normalize_name(item)
                            self.canonical_index[norm] = item
                        elif isinstance(item, dict) and "canonical_name" in item:
                            canonical = item["canonical_name"]
                            self.canonical_entities.add(canonical)
                            norm = self.normalize_name(canonical)
                            self.canonical_index[norm] = canonical
                            compact = re.sub(r'[^a-z0-9]', '', canonical.lower())
                            self.canonical_index[compact] = canonical
                            for alias in item.get("aliases", []):
                                norm_alias = self.normalize_name(alias)
                                self.canonical_index[norm_alias] = canonical
                                compact_alias = re.sub(r'[^a-z0-9]', '', alias.lower())
                                self.canonical_index[compact_alias] = canonical
                                self.canonical_index[alias.strip().lower()] = canonical
        except Exception:
            pass

    def normalize_name(self, name: str) -> str:
        """
        Normalize raw string:
        1. Convert text to lowercase
        2. Strip special punctuation (commas, dots, hyphens)
        3. Remove legal corporate suffixes (Inc, LLC, Ltd, Corp)
        4. Normalize multiple whitespaces
        """
        if not name:
            return ""

        text = name.strip().lower()

        # Remove trailing and inline punctuation like commas, quotes
        text = re.sub(r'[\'\",\.]', ' ', text)

        # Strip corporate suffixes
        for suffix_pat in self.CORPORATE_SUFFIXES:
            text = re.sub(suffix_pat, ' ', text, flags=re.IGNORECASE)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def exact_match(self, name: str) -> Optional[str]:
        """Case-insensitive exact match against canonical entity set."""
        name_lower = name.strip().lower()
        for canonical in self.canonical_entities:
            if canonical.lower() == name_lower:
                return canonical
        return None

    def resolve_entity(self, raw_name: str) -> str:
        """
        Deterministic matching pipeline:
        1. Exact match against known canonical entities.
        2. Normalized match in canonical index.
        3. Known mapping cache lookup.
        4. Fallback to cleaned raw title-case entity name.
        """
        if not raw_name or not raw_name.strip():
            return "Unknown"

        raw_trimmed = raw_name.strip()

        # Step 1: Direct exact match
        direct = self.exact_match(raw_trimmed)
        if direct:
            self.create_mapping(raw_trimmed, direct, matching_method="EXACT_MATCH")
            return direct

        # Step 2: Normalized lookup
        norm = self.normalize_name(raw_trimmed)
        if norm in self.canonical_index:
            canonical = self.canonical_index[norm]
            self.create_mapping(raw_trimmed, canonical, matching_method="NORMALIZED_MATCH")
            return canonical

        # Step 2b: Compact alphanumeric lookup
        compact = re.sub(r'[^a-z0-9]', '', raw_trimmed.lower())
        if compact in self.canonical_index:
            canonical = self.canonical_index[compact]
            self.create_mapping(raw_trimmed, canonical, matching_method="COMPACT_MATCH")
            return canonical

        # Step 3: Previously recorded mapping
        if raw_trimmed in self.mappings:
            return self.mappings[raw_trimmed]

        # Step 4: Unknown entity - register as its own canonical representation
        # Format neatly as Title Case without trailing corporate noise
        clean_fallback = " ".join([word.capitalize() for word in norm.split()]) if norm else raw_trimmed
        self.create_mapping(raw_trimmed, clean_fallback, matching_method="NEW_CANONICAL")
        self.canonical_entities.add(clean_fallback)
        self.canonical_index[norm] = clean_fallback
        return clean_fallback

    def create_mapping(self, raw: str, canonical: str, matching_method: str = "DETERMINISTIC") -> None:
        """Record raw-to-canonical mapping and append to audit log."""
        self.mappings[raw] = canonical
        self.mapping_logs.append({
            "raw_name": raw,
            "canonical_name": canonical,
            "matching_method": matching_method
        })

    def get_canonical_entity(self, name: str) -> Optional[str]:
        """Return canonical entity if registered, else None."""
        norm = self.normalize_name(name)
        return self.canonical_index.get(norm)

    def get_mapping_logs(self) -> List[Dict[str, str]]:
        """Return the complete mapping log for Google Sheets Tab 6."""
        # Deduplicate mapping logs by (raw_name, canonical_name)
        seen = set()
        unique_logs = []
        for entry in self.mapping_logs:
            pair = (entry["raw_name"], entry["canonical_name"])
            if pair not in seen:
                seen.add(pair)
                unique_logs.append(entry)
        return unique_logs
