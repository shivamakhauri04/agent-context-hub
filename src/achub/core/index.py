from __future__ import annotations

import math
import re
from collections import defaultdict

# Synonym map: query token -> related terms that should also match.
# Expanded tokens are weighted at 0.5x to avoid drowning out exact matches.
_SYNONYM_MAP: dict[str, list[str]] = {
    "trade": ["day_trade", "pdt", "transaction", "buy", "sell", "order"],
    "trading": ["day_trade", "pdt", "transaction", "buy", "sell", "order"],
    "tax": ["wash", "harvesting", "irs", "deduction", "loss"],
    "split": ["corporate_action", "ratio", "adjustment", "stock_split"],
    "limit": ["restriction", "threshold", "constraint", "pdt"],
    "restriction": ["limit", "threshold", "constraint", "pdt", "freeze"],
    "violation": ["pdt", "wash", "rule", "regulatory", "compliance"],
    "day": ["day_trade", "pdt", "intraday", "same_day"],
    "another": [],
    "wash": ["wash_sale", "tax", "loss", "irs", "30_day"],
    "sale": ["wash_sale", "sell", "transaction"],
    "margin": ["pdt", "equity", "25000", "account"],
    "hours": ["market_hours", "trading_hours", "session", "premarket", "afterhours"],
    "price": ["adjusted", "close", "ohlc", "quote"],
    "data": ["yfinance", "polygon", "vendor", "api", "feed"],
    "broker": ["alpaca", "interactive_brokers", "api", "order"],
    "vwap": ["volume_weighted", "indicator", "technical"],
    "indicator": ["vwap", "rsi", "macd", "technical"],
    "fractional": ["yfinance", "shares", "partial"],
    "settlement": ["wash_sale", "t2", "clearing"],
    "t2": ["settlement", "clearing", "wash_sale"],
    "premarket": ["trading_hours", "extended_hours"],
    "afterhours": ["trading_hours", "extended_hours"],
    "drip": ["dividend", "reinvestment", "corporate_action"],
    "dividend": ["drip", "corporate_action", "distribution"],
    "stop": ["order", "stop_loss", "alpaca"],
}

_SYNONYM_WEIGHT = 0.5

# Severity boost multipliers applied after TF-IDF scoring.
_SEVERITY_BOOST: dict[str, float] = {
    "critical": 1.5,
    "high": 1.2,
    "medium": 1.0,
    "low": 0.8,
    "info": 0.6,
}


def _stem(token: str) -> str:
    """Simple suffix-stripping stemmer, first-match-wins.

    Applied after lowercasing. Both index and query go through the same
    stemmer, so consistency is guaranteed. Synonym lookup in
    _expand_query_tokens checks the original (pre-stem) form first.
    """
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("es"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    if len(token) > 4 and token.endswith("e"):
        return token[:-1]
    return token


def _tokenize(text: str) -> list[str]:
    """Tokenize text: split on non-alphanumeric, lowercase, then stem."""
    return [_stem(tok.lower()) for tok in re.findall(r"[a-zA-Z0-9_]+", text) if tok]


def _raw_tokens(text: str) -> list[str]:
    """Extract lowercased tokens before stemming (for synonym lookup)."""
    return [tok.lower() for tok in re.findall(r"[a-zA-Z0-9_]+", text) if tok]


def _expand_query_tokens(raw_tokens: list[str]) -> list[tuple[str, float]]:
    """Expand query tokens with synonyms, then stem everything.

    Synonym lookup uses the original (pre-stem) token so that keys like
    "trading" in _SYNONYM_MAP still match. All returned tokens are stemmed
    for consistency with the index.
    """
    expanded: list[tuple[str, float]] = []
    for tok in raw_tokens:
        expanded.append((_stem(tok), 1.0))
        for synonym in _SYNONYM_MAP.get(tok, []):
            expanded.append((_stem(synonym), _SYNONYM_WEIGHT))
    return expanded


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
        """Search the index using TF-IDF scoring with synonym expansion.

        Args:
            query: Search query string.
            limit: Maximum number of results to return.

        Returns:
            List of (content_id, score) tuples sorted by descending score.
        """
        raw = _raw_tokens(query)
        if not raw or not self._docs:
            return []

        expanded = _expand_query_tokens(raw)
        n = len(self._docs)
        scores: dict[str, float] = defaultdict(float)

        for term, weight in expanded:
            if term not in self._doc_freq:
                continue
            df = len(self._doc_freq[term])
            idf = math.log(n / df) if df > 0 else 0.0

            for content_id in self._doc_freq[term]:
                tf = self._tf[content_id].get(term, 0.0)
                scores[content_id] += tf * idf * weight

        # Apply severity boost
        for content_id in scores:
            severity = (
                self._metadata.get(content_id, {})
                .get("severity", "medium")
                .lower()
            )
            boost = _SEVERITY_BOOST.get(severity, 1.0)
            scores[content_id] *= boost

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:limit]
