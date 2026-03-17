from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from achub.core.domain import discover_domains, get_domain_path
from achub.core.index import ContentIndex
from achub.core.parser import parse_all_in_directory

logger = logging.getLogger(__name__)

DEFAULT_STALENESS_THRESHOLD_DAYS = 90


def _content_id_from_path(domain: str, domain_path: Path, filepath: Path) -> str:
    """Derive a content ID like 'trading/regulations/pdt-rule' from a file path."""
    rel = Path(filepath).relative_to(domain_path)
    # Strip the .md extension and join parts with /
    parts = list(rel.parts)
    if parts:
        parts[-1] = parts[-1].removesuffix(".md")
    return domain + "/" + "/".join(parts)


class ContentRegistry:
    """Central registry that indexes all content across domains.

    Call build() once at startup, then reuse search(), get(), and list_all().
    """

    def __init__(
        self,
        base_path: Path,
        extra_content_dirs: list[Path] | None = None,
        staleness_threshold_days: int = DEFAULT_STALENESS_THRESHOLD_DAYS,
    ) -> None:
        self._base_path = Path(base_path)
        self._extra_content_dirs = extra_content_dirs or []
        self._staleness_threshold_days = staleness_threshold_days
        self._content: dict[str, dict] = {}
        self._index = ContentIndex()

    def build(self) -> None:
        """Scan all domains, parse all content, and build the internal index."""
        self._content.clear()
        self._index = ContentIndex()

        # Index built-in domains
        self._index_base(self._base_path)

        # Index extra content directories (enterprise/proprietary content)
        for extra_dir in self._extra_content_dirs:
            extra_path = Path(extra_dir)
            if extra_path.is_dir():
                self._index_base(extra_path)
            else:
                logger.warning("extra_content_dir does not exist: %s", extra_path)

    def _index_base(self, base_path: Path) -> None:
        """Index all domains under a base path."""
        domains = discover_domains(base_path)
        for domain in domains:
            domain_path = get_domain_path(base_path, domain)
            parsed_items = parse_all_in_directory(domain_path)
            for item in parsed_items:
                filepath = Path(item["path"])
                if filepath.name == "DOMAIN.md":
                    continue
                content_id = _content_id_from_path(domain, domain_path, filepath)
                item["content_id"] = content_id
                item["domain"] = domain

                rel = filepath.relative_to(domain_path)
                item["category"] = rel.parts[0] if len(rel.parts) > 1 else None

                self._content[content_id] = item

                metadata = item.get("metadata", {})
                searchable_text = item.get("body", "")
                title = metadata.get("title", "")
                tags = " ".join(metadata.get("tags", []))
                if title:
                    searchable_text = title + " " + searchable_text
                if tags:
                    searchable_text = tags + " " + searchable_text
                self._index.add(content_id, searchable_text, metadata)

    def _annotate_staleness(self, item: dict) -> dict:
        """Add stale/stale_days fields if last_verified is too old."""
        last_verified = item.get("metadata", {}).get("last_verified", "")
        if not last_verified:
            return item
        try:
            if isinstance(last_verified, str):
                verified_date = datetime.strptime(last_verified, "%Y-%m-%d")
            else:
                verified_date = datetime.combine(last_verified, datetime.min.time())
            days_old = (datetime.now() - verified_date).days
            if days_old > self._staleness_threshold_days:
                item = dict(item)
                item["stale"] = True
                item["stale_days"] = days_old
        except (ValueError, TypeError):
            logger.warning(
                "Bad last_verified date format: %r in %s",
                last_verified,
                item.get("content_id", "unknown"),
            )
        return item

    def get(self, content_id: str) -> dict | None:
        """Get content by its ID (e.g. 'trading/regulations/pdt-rule').

        Args:
            content_id: Unique content identifier.

        Returns:
            Content dict or None if not found.
        """
        item = self._content.get(content_id)
        if item is None:
            return None
        return self._annotate_staleness(item)

    def list_all(
        self, domain: str | None = None, category: str | None = None
    ) -> list[dict]:
        """List content items with optional filters.

        Args:
            domain: Filter by domain name.
            category: Filter by category name.

        Returns:
            List of content dicts matching the filters.
        """
        items = list(self._content.values())
        if domain is not None:
            items = [i for i in items if i.get("domain") == domain]
        if category is not None:
            items = [i for i in items if i.get("category") == category]
        return items

    def search(self, query: str, domain: str | None = None) -> list[dict]:
        """Search content using the TF-IDF index.

        Args:
            query: Search query string.
            domain: Optional domain filter.

        Returns:
            List of content dicts with added 'score' key, sorted by relevance.
        """
        results = self._index.search(query)
        output: list[dict] = []
        for content_id, score in results:
            item = self._content.get(content_id)
            if item is None:
                continue
            if domain is not None and item.get("domain") != domain:
                continue
            result = dict(item)
            result["score"] = score
            result = self._annotate_staleness(result)
            output.append(result)
        return output
