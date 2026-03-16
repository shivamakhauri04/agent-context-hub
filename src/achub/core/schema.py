from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from achub.core.parser import parse_content

_DEFAULT_SCHEMA_NAME = "schemas/content-frontmatter.json"


def _find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from start looking for a directory containing pyproject.toml."""
    current = Path(start) if start else Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return None


def _load_schema(schema_path: Path | None = None) -> dict | None:
    """Load a JSON schema file."""
    if schema_path is None:
        root = _find_project_root()
        if root is None:
            return None
        schema_path = root / _DEFAULT_SCHEMA_NAME
    schema_path = Path(schema_path)
    if not schema_path.exists():
        return None
    with open(schema_path) as f:
        return json.load(f)


def validate_frontmatter(
    metadata: dict, schema_path: Path | None = None
) -> list[str]:
    """Validate frontmatter metadata against a JSON schema.

    Args:
        metadata: Frontmatter metadata dict.
        schema_path: Optional path to a JSON schema file. Defaults to
            schemas/content-frontmatter.json relative to the project root.

    Returns:
        List of validation error messages. Empty list means valid.
    """
    schema = _load_schema(schema_path)
    if schema is None:
        return ["Schema file not found; cannot validate."]

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(metadata), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"{path}: {error.message}")
    return errors


def validate_content_file(
    filepath: Path, schema_path: Path | None = None
) -> list[str]:
    """Parse a content file and validate its frontmatter.

    Args:
        filepath: Path to the markdown content file.
        schema_path: Optional path to a JSON schema file.

    Returns:
        List of validation error messages.
    """
    parsed = parse_content(filepath)
    if parsed is None:
        return [f"Failed to parse {filepath}"]
    return validate_frontmatter(parsed["metadata"], schema_path)
