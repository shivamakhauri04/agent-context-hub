from __future__ import annotations

from pathlib import Path

from achub.core.domain import discover_domains, get_domain_path
from achub.core.index import ContentIndex
from achub.core.parser import parse_all_in_directory


def _content_id_from_path(domain: str, domain_path: Path, filepath: Path) -> str:
    """Derive a content ID like 'trading/regulations/pdt-rule' from a file path."""
    rel = Path(filepath).relative_to(domain_path)
    # Strip the .md extension and join parts with /
    parts = list(rel.parts)
    if parts:
        parts[-1] = parts[-1].removesuffix(".md")
    return domain + "/" + "/".join(parts)


class ContentRegistry:
    """Central registry that indexes all content across domains."""

    def __init__(self, base_path: Path) -> None:
        self._base_path = Path(base_path)
        self._content: dict[str, dict] = {}
        self._index = ContentIndex()

    def build(self) -> None:
        """Scan all domains, parse all content, and build the internal index."""
        self._content.clear()
        self._index = ContentIndex()

        domains = discover_domains(self._base_path)
        for domain in domains:
            domain_path = get_domain_path(self._base_path, domain)
            parsed_items = parse_all_in_directory(domain_path)
            for item in parsed_items:
                filepath = Path(item["path"])
                # Skip DOMAIN.md itself from content listing
                if filepath.name == "DOMAIN.md":
                    continue
                content_id = _content_id_from_path(domain, domain_path, filepath)
                item["content_id"] = content_id
                item["domain"] = domain

                # Derive category from first subdirectory under domain
                rel = filepath.relative_to(domain_path)
                item["category"] = rel.parts[0] if len(rel.parts) > 1 else None

                self._content[content_id] = item

                # Index the body and metadata title for search
                searchable_text = item.get("body", "")
                title = item.get("metadata", {}).get("title", "")
                if title:
                    searchable_text = title + " " + searchable_text
                self._index.add(content_id, searchable_text, item.get("metadata", {}))

    def get(self, content_id: str) -> dict | None:
        """Get content by its ID (e.g. 'trading/regulations/pdt-rule').

        Args:
            content_id: Unique content identifier.

        Returns:
            Content dict or None if not found.
        """
        return self._content.get(content_id)

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
            output.append(result)
        return output
