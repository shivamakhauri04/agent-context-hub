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
        result = {
            "metadata": dict(post.metadata),
            "body": post.content,
            "path": str(filepath),
        }
        checks = _extract_structured_checks(post.content)
        if checks is not None:
            result["checks"] = checks
        return result
    except Exception as exc:
        warnings.warn(f"Failed to parse {filepath}: {exc}")
        logger.warning("Malformed YAML frontmatter in %s: %s", filepath, exc)
        return None


def _extract_structured_checks(body: str) -> list[dict] | None:
    """Extract structured checks YAML block from content body."""
    import yaml as _yaml

    lines = body.splitlines()
    in_section = False
    in_yaml_block = False
    yaml_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "## structured checks":
            in_section = True
            continue
        if in_section and not in_yaml_block:
            if stripped.startswith("```yaml") or stripped.startswith("```yml"):
                in_yaml_block = True
                continue
            if stripped.startswith("## "):
                break
        if in_section and in_yaml_block:
            if stripped == "```":
                break
            yaml_lines.append(line)

    if not yaml_lines:
        return None

    try:
        data = _yaml.safe_load("\n".join(yaml_lines))
        if isinstance(data, dict) and "checks" in data:
            return data["checks"]
    except Exception:
        logger.warning("Failed to parse structured checks YAML block", exc_info=True)
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
