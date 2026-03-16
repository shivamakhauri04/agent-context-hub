from __future__ import annotations

import logging
import warnings
from pathlib import Path

import frontmatter

logger = logging.getLogger(__name__)


def parse_content(filepath: Path) -> dict | None:
    """Parse a markdown file with YAML frontmatter.

    Args:
        filepath: Path to the markdown file.

    Returns:
        Dict with keys "metadata", "body", and "path", or None if parsing fails.
    """
    filepath = Path(filepath)
    try:
        post = frontmatter.load(filepath)
        return {
            "metadata": dict(post.metadata),
            "body": post.content,
            "path": str(filepath),
        }
    except Exception as exc:
        warnings.warn(f"Failed to parse {filepath}: {exc}")
        logger.warning("Malformed YAML frontmatter in %s: %s", filepath, exc)
        return None


def parse_all_in_directory(directory: Path) -> list[dict]:
    """Recursively find and parse all .md files in a directory.

    Args:
        directory: Root directory to search.

    Returns:
        List of parsed content dicts (skips files that fail to parse).
    """
    directory = Path(directory)
    results: list[dict] = []
    for md_file in sorted(directory.rglob("*.md")):
        parsed = parse_content(md_file)
        if parsed is not None:
            results.append(parsed)
    return results
