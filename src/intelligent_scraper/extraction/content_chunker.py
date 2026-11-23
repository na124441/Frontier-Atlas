"""
Intelligent Content Chunker.
Prevents oversized LLM payloads and handles HTTP 413 through semantic chunking and result merging.
Adheres to SRS FR-10 and LLD Section 5.4.
"""

import re
from typing import Any, Dict, List, Optional


class ContentChunker:
    """Estimates tokens, divides text semantically, and merges partial extractions."""

    def __init__(self, max_tokens: int = 3500, overlap_tokens: int = 200):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def estimate_tokens(self, text: str) -> int:
        """
        Heuristic token estimator (approx 4 characters per token for English text).
        Avoids heavy tokenizer dependencies.
        """
        if not text:
            return 0
        return max(1, len(text) // 4)

    def split_content(self, text: str, max_tokens: Optional[int] = None) -> List[str]:
        """
        Splits oversized text using heading and paragraph boundaries:
        1. Split on major section headings or double newlines.
        2. Combine segments up to max_tokens.
        """
        budget = max_tokens or self.max_tokens
        if not text or self.estimate_tokens(text) <= budget:
            return [text] if text else []

        # Split on double newlines / paragraph breaks
        paragraphs = re.split(r'\n{2,}', text)
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_tokens = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_tokens = self.estimate_tokens(para)

            # If a single paragraph exceeds budget, split on single newlines or sentence boundaries
            if para_tokens > budget:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_tokens = 0

                sentences = re.split(r'(?<=[.!?])\s+', para)
                sub_chunk: List[str] = []
                sub_tokens = 0
                for s in sentences:
                    st = self.estimate_tokens(s)
                    if sub_tokens + st > budget and sub_chunk:
                        chunks.append(" ".join(sub_chunk))
                        sub_chunk = [s]
                        sub_tokens = st
                    else:
                        sub_chunk.append(s)
                        sub_tokens += st
                if sub_chunk:
                    chunks.append(" ".join(sub_chunk))
                continue

            if current_tokens + para_tokens > budget and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def create_chunks(self, text: str) -> List[str]:
        """Alias for split_content with default instance budget."""
        return self.split_content(text, self.max_tokens)

    def merge_chunk_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merges partial extraction dictionaries extracted from multiple chunks.
        Combines lists (authors, products), preserves longest strings for descriptions,
        and uses non-null values.
        """
        if not results:
            return {}
        if len(results) == 1:
            return results[0]

        merged: Dict[str, Any] = {}

        for item in results:
            if not isinstance(item, dict):
                continue
            for k, v in item.items():
                if v is None:
                    continue
                if k not in merged or merged[k] is None:
                    merged[k] = v
                elif isinstance(merged[k], list) and isinstance(v, list):
                    # Combine and deduplicate lists
                    combined = merged[k] + [elem for elem in v if elem not in merged[k]]
                    merged[k] = combined
                elif isinstance(merged[k], str) and isinstance(v, str):
                    # Keep longer/more informative text
                    if len(v) > len(merged[k]):
                        merged[k] = v
                elif isinstance(merged[k], (int, float)) and isinstance(v, (int, float)):
                    # Keep non-zero / higher value (e.g. employee count or star count)
                    merged[k] = max(merged[k], v)

        return merged
