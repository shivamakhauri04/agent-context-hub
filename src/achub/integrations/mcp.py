"""MCP server integration for agent-context-hub.

Exposes achub content as MCP tools for Claude and other MCP-compatible agents.
Requires: pip install agent-context-hub[mcp]
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from achub.commands.check import _RULE_CHECKERS
from achub.core.constants import SKIP_SECTIONS
from achub.core.registry import ContentRegistry
from achub.prompts import get_system_prompt
from achub.utils.paths import find_project_root

logger = logging.getLogger(__name__)

# Sections to skip in LLM-optimized output (shared constant).
_SKIP_SECTIONS = SKIP_SECTIONS

_SNIPPET_LENGTH = 500


def _build_registry() -> ContentRegistry:
    """Build and return a ContentRegistry instance."""
    root = find_project_root()
    config = _load_achub_config(root)
    extra_dirs = [Path(p) for p in config.get("extra_content", [])]
    staleness = config.get("staleness_threshold_days", 90)
    registry = ContentRegistry(
        root, extra_content_dirs=extra_dirs, staleness_threshold_days=staleness
    )
    registry.build()
    return registry


def _load_achub_config(root: Path) -> dict:
    """Load achub.yaml config from project root if it exists."""
    config_path = root / "achub.yaml"
    if not config_path.exists():
        config_path = root / "achub.yml"
    if not config_path.exists():
        return {}
    try:
        import yaml

        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        logger.warning("Failed to parse %s, returning empty config", config_path, exc_info=True)
        return {}


def _format_llm(content: dict) -> str:
    """Format content for LLM consumption: skip non-actionable sections."""
    metadata = content.get("metadata", {})
    body = content.get("body", "")

    lines = [f"# {metadata.get('title', content.get('content_id', 'Untitled'))}"]
    lines.append(f"Severity: {metadata.get('severity', 'unknown')}")

    # Staleness warning
    if content.get("stale"):
        stale_days = content.get("stale_days", "?")
        lines.append(
            f"WARNING: STALE ({stale_days} days since last verification)"
            " — verify against primary sources"
        )

    lines.append("")
    in_section = True  # Start including content before first header
    for line in body.splitlines():
        if line.startswith("#"):
            heading_text = line.lstrip("#").strip().lower()
            if heading_text in _SKIP_SECTIONS:
                in_section = False
            else:
                in_section = True
                lines.append(line)
        elif in_section and line.strip():
            lines.append(line)

    return "\n".join(lines)


def create_server():
    """Create and configure the MCP server with all tools."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP(
        "agent-context-hub",
        instructions=(
            "Agent-readable knowledge layer for AI agents. "
            "Call achub_prompt first to get mandatory check instructions "
            "for your domain. Then use search, retrieve, and check tools "
            "to prevent hallucinations in trading and other high-stakes domains."
        ),
    )

    registry = _build_registry()

    @server.tool()
    def achub_search(
        query: str,
        domain: str | None = None,
        include_body: bool = False,
    ) -> str:
        """Search the agent-context-hub knowledge base for domain-specific rules,
        regulations, and gotchas. Returns ranked results by relevance.

        Args:
            query: Natural language search query.
            domain: Optional domain filter (e.g. "trading").
            include_body: If True, include a snippet of each result's body.
        """
        results = registry.search(query, domain=domain)
        if not results:
            return json.dumps({"results": [], "message": "No results found."})
        output = []
        for item in results[:10]:
            entry: dict = {
                "id": item.get("content_id", ""),
                "title": item.get("metadata", {}).get("title", ""),
                "score": round(item.get("score", 0.0), 4),
                "severity": item.get("metadata", {}).get("severity", ""),
                "domain": item.get("domain", ""),
            }
            if item.get("stale"):
                entry["stale"] = True
                entry["stale_days"] = item.get("stale_days")
            if include_body:
                body = item.get("body", "")
                entry["snippet"] = body[:_SNIPPET_LENGTH]
            output.append(entry)
        return json.dumps({"results": output})

    @server.tool()
    def achub_search_and_get(
        query: str,
        domain: str | None = None,
        min_score: float = 0.01,
    ) -> str:
        """Search and return the top result with full LLM-formatted body.

        Single call that combines search + get for the best match.
        Use this when you need the actual content, not just IDs.
        Returns a JSON envelope with content_id, score, severity, and content.

        Args:
            query: Natural language search query.
            domain: Optional domain filter (e.g. "trading").
            min_score: Minimum score threshold (default 0.01).
        """
        results = registry.search(query, domain=domain)
        if not results:
            return json.dumps({"error": "No results found."})
        top = results[0]
        score = top.get("score", 0.0)
        envelope: dict = {
            "content_id": top.get("content_id", ""),
            "score": round(score, 4),
            "severity": top.get("metadata", {}).get("severity", ""),
            "content": _format_llm(top),
        }
        if top.get("stale"):
            envelope["stale"] = True
            envelope["stale_days"] = top.get("stale_days")
        if score < min_score:
            envelope["warning"] = "Low confidence match"
        return json.dumps(envelope)

    @server.tool()
    def achub_get(content_id: str, format: str = "llm") -> str:
        """Retrieve a specific content document by its ID.

        Args:
            content_id: Document ID (e.g. "trading/regulations/pdt-rule/rules").
            format: Output format — "llm" (token-efficient, default), "json"
                    (structured), or "markdown" (full body).
        """
        content = registry.get(content_id)
        if content is None:
            return json.dumps({"error": f"Content not found: {content_id}"})

        metadata = content.get("metadata", {})
        body = content.get("body", "")

        if format == "json":
            result: dict = {
                "content_id": content.get("content_id"),
                "metadata": metadata,
                "body": body,
            }
            if content.get("stale"):
                result["stale"] = True
                result["stale_days"] = content.get("stale_days")
            return json.dumps(result)
        elif format == "markdown":
            prefix = ""
            if content.get("stale"):
                stale_days = content.get("stale_days", "?")
                prefix = (
                    f"> WARNING: STALE ({stale_days} days) "
                    "— verify against primary sources\n\n"
                )
            return prefix + body
        else:
            return _format_llm(content)

    @server.tool()
    def achub_check(domain: str, rules: str, portfolio_json: str) -> str:
        """Run compliance rule checks against a portfolio.

        Runs both hardcoded Python checkers and structured YAML checks
        from content documents.

        Args:
            domain: Domain to check (e.g. "trading").
            rules: Comma-separated rule names (e.g. "pdt,wash-sale").
            portfolio_json: JSON string of portfolio state.
        """
        try:
            portfolio = json.loads(portfolio_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON: {e}"})

        rule_names = [r.strip() for r in rules.split(",")]
        violations = []
        passed_rules = []
        check_warnings: list[str] = []

        # Python checkers
        for rule_name in rule_names:
            checker = _RULE_CHECKERS.get(rule_name)
            if checker is None:
                violations.append(f"Unknown rule: {rule_name}")
                continue
            result = checker(portfolio)
            if result:
                violations.extend(result)
            else:
                passed_rules.append(rule_name)

        # Structured checks from content documents
        try:
            from achub.core.checker import StructuredCheckEvaluator

            evaluator = StructuredCheckEvaluator()
            items = registry.list_all(domain=domain)
            for item in items:
                checks = item.get("checks", [])
                if not checks:
                    continue
                results = evaluator.evaluate_checks(checks, portfolio)
                for r in results:
                    if not r.passed:
                        violations.append(
                            f"[{r.severity.upper()}] {r.id}: {r.message}"
                        )
        except Exception as exc:
            logger.warning("Structured check evaluation failed", exc_info=True)
            check_warnings.append(
                f"Structured check evaluation failed: {exc}. "
                "Only Python checker results are shown."
            )

        result_dict: dict = {
            "violations": violations,
            "passed": passed_rules,
            "has_violations": len(violations) > 0,
        }
        if check_warnings:
            result_dict["warnings"] = check_warnings
        return json.dumps(result_dict)

    @server.tool()
    def achub_list(
        domain: str | None = None, category: str | None = None
    ) -> str:
        """List available content documents with optional filters.

        Args:
            domain: Filter by domain (e.g. "trading").
            category: Filter by category (e.g. "regulations").
        """
        items = registry.list_all(domain=domain, category=category)
        output = []
        for item in items:
            metadata = item.get("metadata", {})
            output.append({
                "id": item.get("content_id", ""),
                "title": metadata.get("title", ""),
                "domain": item.get("domain", ""),
                "category": item.get("category", ""),
                "severity": metadata.get("severity", ""),
            })
        return json.dumps({"items": output, "count": len(output)})

    @server.tool()
    def achub_prompt(domain: str) -> str:
        """Get mandatory check instructions for a domain.

        Call this FIRST when starting work in a domain. Returns a system
        prompt snippet listing CRITICAL and HIGH severity documents that
        the agent must consult before taking actions.

        Args:
            domain: Domain name (e.g. "trading").
        """
        return get_system_prompt(domain, registry)

    return server


def run_server(transport: str = "stdio"):
    """Run the MCP server with the specified transport."""
    server = create_server()
    server.run(transport=transport)
