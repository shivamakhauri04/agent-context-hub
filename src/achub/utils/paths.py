"""Shared path utilities for agent-context-hub."""
from __future__ import annotations

import importlib.resources
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Find the project root containing domains/ and schemas/.

    Checks three locations in order:
    1. Walk up from `start` (or CWD) looking for pyproject.toml
    2. Walk up from this file looking for pyproject.toml (dev install)
    3. Fall back to installed package data via importlib.resources

    Returns:
        Path to the project root or installed package data directory.
    """
    # Strategy 1: walk up from explicit start path
    if start is not None:
        found = _walk_up_for_pyproject(Path(start))
        if found is not None:
            return found

    # Strategy 2: walk up from this source file (works in dev/editable install)
    found = _walk_up_for_pyproject(Path(__file__).resolve().parent)
    if found is not None:
        return found

    # Strategy 3: installed package — domains/ bundled inside achub package
    try:
        pkg_root = importlib.resources.files("achub")
        pkg_path = Path(str(pkg_root))
        if (pkg_path / "domains").is_dir():
            return pkg_path
    except (TypeError, ModuleNotFoundError):
        pass

    # Last resort: current working directory
    return Path.cwd()


def find_domains_dir(project_root: Path) -> Path:
    """Return the domains directory, checking both project root and package data."""
    candidate = project_root / "domains"
    if candidate.is_dir():
        return candidate
    # Installed package case: domains inside the achub package
    try:
        pkg_root = importlib.resources.files("achub")
        pkg_path = Path(str(pkg_root))
        candidate = pkg_path / "domains"
        if candidate.is_dir():
            return candidate
    except (TypeError, ModuleNotFoundError):
        pass
    # Fall back to original path even if it doesn't exist
    return project_root / "domains"


def find_schemas_dir(project_root: Path) -> Path:
    """Return the schemas directory, checking both project root and package data."""
    candidate = project_root / "schemas"
    if candidate.is_dir():
        return candidate
    try:
        pkg_root = importlib.resources.files("achub")
        pkg_path = Path(str(pkg_root))
        candidate = pkg_path / "schemas"
        if candidate.is_dir():
            return candidate
    except (TypeError, ModuleNotFoundError):
        pass
    return project_root / "schemas"


def _walk_up_for_pyproject(start: Path) -> Path | None:
    """Walk up directories from start looking for pyproject.toml."""
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return None
