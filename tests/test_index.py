from __future__ import annotations

from achub.core.index import ContentIndex


def test_add_and_search() -> None:
    """Adding 3 docs about different topics, searching returns the relevant one first."""
    idx = ContentIndex()
    idx.add("doc-splits", "stock split adjustment ratio shares price", {"title": "Stock Splits"})
    idx.add("doc-pdt", "pattern day trader margin equity finra regulation", {"title": "PDT Rule"})
    idx.add("doc-wash", "wash sale loss 30 day window tax disallowed", {"title": "Wash Sale"})

    results = idx.search("stock split")
    assert len(results) > 0
    assert results[0][0] == "doc-splits"


def test_search_empty_index() -> None:
    """Searching an empty index returns an empty list."""
    idx = ContentIndex()
    results = idx.search("anything")
    assert results == []


def test_search_with_limit() -> None:
    """Limiting results to 1 returns only 1 result."""
    idx = ContentIndex()
    idx.add("doc-a", "stock market trading shares", {"title": "A"})
    idx.add("doc-b", "stock exchange listed securities", {"title": "B"})
    idx.add("doc-c", "stock split forward reverse", {"title": "C"})

    results = idx.search("stock", limit=1)
    assert len(results) == 1


def test_search_relevance() -> None:
    """A document with more query term mentions scores higher."""
    idx = ContentIndex()
    # doc-many has "split" mentioned multiple times
    idx.add(
        "doc-many",
        "split split split stock split adjustment split ratio",
        {"title": "Many Splits"},
    )
    # doc-few has "split" mentioned once
    idx.add(
        "doc-few",
        "stock market trading is fun and exciting every day",
        {"title": "Few Splits"},
    )

    results = idx.search("split")
    assert len(results) >= 1
    assert results[0][0] == "doc-many"
