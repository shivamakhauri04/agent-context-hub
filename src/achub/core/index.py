from __future__ import annotations

import math
import re
from collections import defaultdict


def _tokenize(text: str) -> list[str]:
    """Tokenize text by splitting on whitespace and punctuation, lowercased."""
    return [tok.lower() for tok in re.findall(r"[a-zA-Z0-9]+", text) if tok]


class ContentIndex:
    """Simple TF-IDF search index using only the math module."""

    def __init__(self) -> None:
        # content_id -> list of tokens
        self._docs: dict[str, list[str]] = {}
        # content_id -> metadata
        self._metadata: dict[str, dict] = {}
        # term -> set of content_ids containing the term
        self._doc_freq: dict[str, set[str]] = defaultdict(set)
        # content_id -> {term: tf}
        self._tf: dict[str, dict[str, float]] = {}

    @property
    def doc_count(self) -> int:
        return len(self._docs)

    def add(self, content_id: str, text: str, metadata: dict) -> None:
        """Add a document to the index.

        Args:
            content_id: Unique identifier for the content.
            text: Full text to index.
            metadata: Associated metadata dict.
        """
        tokens = _tokenize(text)
        self._docs[content_id] = tokens
        self._metadata[content_id] = metadata

        # Compute term frequency (normalized by doc length)
        tf: dict[str, float] = {}
        if tokens:
            counts: dict[str, int] = defaultdict(int)
            for tok in tokens:
                counts[tok] += 1
            for term, count in counts.items():
                tf[term] = count / len(tokens)
                self._doc_freq[term].add(content_id)
        self._tf[content_id] = tf

    def search(self, query: str, limit: int = 10) -> list[tuple[str, float]]:
        """Search the index using TF-IDF scoring.

        Args:
            query: Search query string.
            limit: Maximum number of results to return.

        Returns:
            List of (content_id, score) tuples sorted by descending score.
        """
        query_tokens = _tokenize(query)
        if not query_tokens or not self._docs:
            return []

        n = len(self._docs)
        scores: dict[str, float] = defaultdict(float)

        for term in query_tokens:
            if term not in self._doc_freq:
                continue
            # IDF: log(N / df)
            df = len(self._doc_freq[term])
            idf = math.log(n / df) if df > 0 else 0.0

            for content_id in self._doc_freq[term]:
                tf = self._tf[content_id].get(term, 0.0)
                scores[content_id] += tf * idf

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:limit]
