"""Tests for domain.py — domain discovery and info retrieval."""
from __future__ import annotations

from pathlib import Path

from achub.core.domain import discover_domains, get_domain_info, get_domain_path


def _make_domain(tmp_path: Path, name: str) -> None:
    """Helper to create a minimal domain directory with DOMAIN.md."""
    domain_dir = tmp_path / "domains" / name
    domain_dir.mkdir(parents=True)
    (domain_dir / "DOMAIN.md").write_text(
        f"---\nname: {name}\ndescription: Test domain {name}\n---\n# {name}\n"
    )


class TestDiscoverDomains:
    def test_discovers_domains_with_domain_md(self, tmp_path: Path):
        """Finds dirs containing DOMAIN.md."""
        _make_domain(tmp_path, "alpha")
        _make_domain(tmp_path, "beta")
        result = discover_domains(tmp_path)
        assert "alpha" in result
        assert "beta" in result

    def test_ignores_dirs_without_domain_md(self, tmp_path: Path):
        """Skips dirs missing DOMAIN.md."""
        _make_domain(tmp_path, "valid")
        (tmp_path / "domains" / "no-domain-md").mkdir(parents=True)
        result = discover_domains(tmp_path)
        assert "valid" in result
        assert "no-domain-md" not in result

    def test_discovers_returns_sorted(self, tmp_path: Path):
        """Domains returned in alphabetical order."""
        for name in ["charlie", "alpha", "bravo"]:
            _make_domain(tmp_path, name)
        result = discover_domains(tmp_path)
        assert result == sorted(result)


class TestGetDomainPath:
    def test_get_domain_path_correct(self, tmp_path: Path):
        """Returns domains/<name> path."""
        path = get_domain_path(tmp_path, "trading")
        assert path == tmp_path / "domains" / "trading"


class TestGetDomainInfo:
    def test_get_domain_info_parsed(self, tmp_path: Path):
        """Parses DOMAIN.md metadata."""
        _make_domain(tmp_path, "test")
        info = get_domain_info(tmp_path, "test")
        assert info is not None
        assert info["metadata"]["name"] == "test"

    def test_get_domain_info_missing_returns_none(self, tmp_path: Path):
        """Missing domain returns None."""
        (tmp_path / "domains").mkdir(parents=True)
        info = get_domain_info(tmp_path, "nonexistent")
        assert info is None
