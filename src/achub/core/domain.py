from __future__ import annotations

from pathlib import Path

from achub.core.parser import parse_content
from achub.utils.paths import find_domains_dir

DEFAULT_DOMAINS_DIR = "domains"


def discover_domains(base_path: Path) -> list[str]:
    """Find all subdirectories under domains/ that contain a DOMAIN.md file.

    Args:
        base_path: Project root path.

    Returns:
        Sorted list of domain names.
    """
    domains_dir = find_domains_dir(base_path)
    if not domains_dir.is_dir():
        return []
    domains: list[str] = []
    for child in sorted(domains_dir.iterdir()):
        if child.is_dir() and (child / "DOMAIN.md").exists():
            domains.append(child.name)
    return domains


def get_domain_path(base_path: Path, domain: str) -> Path:
    """Return the path to a domain directory.

    Args:
        base_path: Project root path.
        domain: Domain name.

    Returns:
        Path to the domain directory.
    """
    return find_domains_dir(base_path) / domain


def get_domain_info(base_path: Path, domain: str) -> dict | None:
    """Parse the DOMAIN.md file for a given domain and return its info.

    Args:
        base_path: Project root path.
        domain: Domain name.

    Returns:
        Parsed content dict from DOMAIN.md, or None if not found/parseable.
    """
    domain_md = get_domain_path(base_path, domain) / "DOMAIN.md"
    if not domain_md.exists():
        return None
    return parse_content(domain_md)
