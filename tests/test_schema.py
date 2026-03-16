from __future__ import annotations

from pathlib import Path

import pytest

from achub.core.parser import parse_content
from achub.core.schema import validate_frontmatter


def test_validate_valid_frontmatter(schemas_dir: Path) -> None:
    """Valid metadata passes validation (empty error list)."""
    schema_path = schemas_dir / "content-frontmatter.json"
    metadata = {
        "id": "test-domain/category/topic/rules",
        "title": "A Valid Test Rule",
        "domain": "test-domain",
        "version": "1.0.0",
        "category": "category",
        "tags": ["test"],
        "severity": "medium",
        "last_verified": "2026-03-01",
    }
    errors = validate_frontmatter(metadata, schema_path=schema_path)
    assert errors == []


def test_validate_missing_required_field(schemas_dir: Path) -> None:
    """Metadata without 'title' fails validation."""
    schema_path = schemas_dir / "content-frontmatter.json"
    metadata = {
        "id": "test-domain/category/topic/rules",
        # "title" is intentionally missing
        "domain": "test-domain",
        "version": "1.0.0",
        "category": "category",
        "tags": ["test"],
        "severity": "medium",
        "last_verified": "2026-03-01",
    }
    errors = validate_frontmatter(metadata, schema_path=schema_path)
    assert len(errors) > 0
    assert any("title" in e for e in errors)


def test_validate_invalid_severity(schemas_dir: Path) -> None:
    """severity='unknown' fails validation."""
    schema_path = schemas_dir / "content-frontmatter.json"
    metadata = {
        "id": "test-domain/category/topic/rules",
        "title": "Some Test Rule",
        "domain": "test-domain",
        "version": "1.0.0",
        "category": "category",
        "tags": ["test"],
        "severity": "unknown",
        "last_verified": "2026-03-01",
    }
    errors = validate_frontmatter(metadata, schema_path=schema_path)
    assert len(errors) > 0
    assert any("severity" in e for e in errors)


def _collect_trading_content_files(domains_dir: Path) -> list[Path]:
    """Collect all .md content files in domains/trading/ (excluding DOMAIN.md)."""
    trading_dir = domains_dir / "trading"
    if not trading_dir.exists():
        return []
    return [f for f in sorted(trading_dir.rglob("*.md")) if f.name != "DOMAIN.md"]


@pytest.mark.parametrize(
    "content_file",
    _collect_trading_content_files(
        Path(__file__).resolve().parent.parent / "domains"
    ),
    ids=lambda p: str(p.relative_to(p.parents[3])),
)
def test_validate_real_content_files(content_file: Path, schemas_dir: Path) -> None:
    """All content files in domains/trading/ pass schema validation."""
    schema_path = schemas_dir / "content-frontmatter.json"
    parsed = parse_content(content_file)
    assert parsed is not None, f"Failed to parse {content_file}"

    errors = validate_frontmatter(parsed["metadata"], schema_path=schema_path)
    assert errors == [], f"Validation errors in {content_file}: {errors}"
