"""MCP server integration for agent-context-hub.

Exposes achub content as MCP tools for Claude and other MCP-compatible agents.
Requires: pip install agent-context-hub[mcp]
"""
from __future__ import annotations

import json
from pathlib import Path

from achub.commands.check import _RULE_CHECKERS
from achub.core.registry import ContentRegistry


def _find_project_root() -> Path:
    """Walk up from this file to find the repo root (contains pyproject.toml)."""
    path = Path(__file__).resolve().parent
    while path != path.parent:
        if (path / "pyproject.toml").exists():
            return path
        path = path.parent
    return Path.cwd()


def _build_registry() -> ContentRegistry:
    """Build and return a ContentRegistry instance."""
    root = _find_project_root()
    registry = ContentRegistry(root)
    registry.build()
    return registry


def create_server():
    """Create and configure the MCP server with all tools."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP(
        "agent-context-hub",
        instructions=(
            "Agent-readable knowledge layer for AI agents. "
            "Search, retrieve, and check domain-specific content "
            "to prevent hallucinations in trading and other high-stakes domains."
        ),
    )

    registry = _build_registry()

    @server.tool()
    def achub_search(query: str, domain: str | None = None) -> str:
        """Search the agent-context-hub knowledge base for domain-specific rules,
        regulations, and gotchas. Returns ranked results by relevance.

        Args:
            query: Natural language search query.
            domain: Optional domain filter (e.g. "trading").
        """
        results = registry.search(query, domain=domain)
        if not results:
            return json.dumps({"results": [], "message": "No results found."})
        output = []
        for item in results[:10]:
            output.append({
                "id": item.get("content_id", ""),
                "title": item.get("metadata", {}).get("title", ""),
                "score": round(item.get("score", 0.0), 4),
                "severity": item.get("metadata", {}).get("severity", ""),
                "domain": item.get("domain", ""),
            })
        return json.dumps({"results": output})

    @server.tool()
    def achub_get(content_id: str, format: str = "llm") -> str:
        """Retrieve a specific content document by its ID.

        Args:
            content_id: Document ID (e.g. "trading/regulations/pdt-rule/rules").
            format: Output format — "llm" (token-efficient, default), "json" (structured),
                    or "markdown" (full body).
        """
        content = registry.get(content_id)
        if content is None:
            return json.dumps({"error": f"Content not found: {content_id}"})

        metadata = content.get("metadata", {})
        body = content.get("body", "")

        if format == "json":
            return json.dumps({
                "content_id": content.get("content_id"),
                "metadata": metadata,
                "body": body,
            })
        elif format == "markdown":
            return body
        else:
            # LLM format: title + actionable sections only
            lines = [f"# {metadata.get('title', content_id)}"]
            lines.append(f"Severity: {metadata.get('severity', 'unknown')}")
            lines.append("")
            in_relevant = False
            for line in body.splitlines():
                stripped = line.strip().lower()
                if line.startswith("#"):
                    is_relevant = any(
                        kw in stripped
                        for kw in [
                            "rule", "checklist", "requirement",
                            "key point", "warning", "constraint", "limit",
                        ]
                    )
                    if is_relevant:
                        in_relevant = True
                        lines.append(line)
                    else:
                        in_relevant = False
                elif in_relevant and line.strip():
                    lines.append(line)
                elif line.strip().startswith("- ") or line.strip().startswith("* "):
                    lines.append(line)
            return "\n".join(lines)

    @server.tool()
    def achub_check(domain: str, rules: str, portfolio_json: str) -> str:
        """Run compliance rule checks against a portfolio.

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

        return json.dumps({
            "violations": violations,
            "passed": passed_rules,
            "has_violations": len(violations) > 0,
        })

    @server.tool()
    def achub_list(domain: str | None = None, category: str | None = None) -> str:
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

    return server


def run_server(transport: str = "stdio"):
    """Run the MCP server with the specified transport."""
    server = create_server()
    server.run(transport=transport)
