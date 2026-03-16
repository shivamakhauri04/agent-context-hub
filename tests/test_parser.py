from __future__ import annotations

from pathlib import Path

import pytest

from achub.core.parser import parse_all_in_directory, parse_content


def test_parse_content_valid(domains_dir: Path) -> None:
    """Parsing a real content file returns metadata with expected fields."""
    filepath = domains_dir / "trading" / "regulations" / "pdt-rule" / "rules.md"
    result = parse_content(filepath)

    assert result is not None
    assert "metadata" in result
    assert "body" in result
    assert "path" in result
    assert "id" in result["metadata"]
    assert "title" in result["metadata"]
    assert "domain" in result["metadata"]
    assert "severity" in result["metadata"]


def test_parse_content_returns_body(domains_dir: Path) -> None:
    """Parsed content body is non-empty."""
    filepath = domains_dir / "trading" / "regulations" / "pdt-rule" / "rules.md"
    result = parse_content(filepath)

    assert result is not None
    assert isinstance(result["body"], str)
    assert len(result["body"]) > 0


def test_parse_all_in_directory(domains_dir: Path) -> None:
    """parse_all_in_directory finds multiple files in domains/trading/."""
    trading_dir = domains_dir / "trading"
    results = parse_all_in_directory(trading_dir)

    # trading/ has DOMAIN.md plus several content files
    assert len(results) > 1
    # Each result should have the expected keys
    for item in results:
        assert "metadata" in item
        assert "body" in item
        assert "path" in item


def test_parse_malformed_yaml(tmp_path: Path) -> None:
    """Parsing a file with malformed YAML frontmatter returns None."""
    bad_file = tmp_path / "bad.md"
    bad_file.write_text(
        "---\n"
        "title: [unclosed bracket\n"
        "  - missing colon value\n"
        "---\n\n"
        "Body text.\n"
    )

    with pytest.warns(UserWarning):
        result = parse_content(bad_file)

    assert result is None
