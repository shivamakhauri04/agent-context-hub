"""System prompt generation for agent-context-hub.

Generates domain-specific mandatory-check instructions that tell agents
WHEN and WHY to call achub tools.
"""
from __future__ import annotations

from achub.core.registry import ContentRegistry


def get_system_prompt(domain: str, registry: ContentRegistry) -> str:
    """Generate a system prompt with mandatory achub check instructions.

    Args:
        domain: Domain name (e.g. "trading").
        registry: A built ContentRegistry instance.

    Returns:
        System prompt string with domain-specific instructions.
    """
    items = registry.list_all(domain=domain)
    if not items:
        return f"No content found for domain '{domain}'."

    critical_docs: list[str] = []
    high_docs: list[str] = []
    other_docs: list[str] = []

    for item in items:
        meta = item.get("metadata", {})
        title = meta.get("title", item.get("content_id", ""))
        severity = meta.get("severity", "").upper()
        tags = ", ".join(meta.get("tags", []))
        line = f"- {title}"
        if tags:
            line += f" (tags: {tags})"

        if severity == "CRITICAL":
            critical_docs.append(line)
        elif severity == "HIGH":
            high_docs.append(line)
        else:
            other_docs.append(line)

    sections: list[str] = []
    sections.append(
        f"MANDATORY: Before executing any action in the '{domain}' domain, "
        "ALWAYS call achub_search or achub_search_and_get to check for "
        "applicable rules and constraints."
    )
    sections.append("")

    if critical_docs:
        sections.append("CRITICAL documents (HARD CONSTRAINTS — never skip):")
        sections.extend(critical_docs)
        sections.append("")

    if high_docs:
        sections.append("HIGH severity documents (check before first use):")
        sections.extend(high_docs)
        sections.append("")

    if other_docs:
        sections.append("Other available knowledge:")
        sections.extend(other_docs)
        sections.append("")

    sections.append(
        "When a document is marked CRITICAL, treat its rules as hard "
        "constraints. Do NOT proceed with an action that would violate them."
    )
    sections.append("")
    sections.append(
        "If a result is marked STALE, warn the user and recommend "
        "verifying against primary sources before relying on it."
    )

    return "\n".join(sections)
