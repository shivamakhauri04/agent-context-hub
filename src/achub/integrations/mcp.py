"""MCP server integration for agent-context-hub.

Exposes achub content as MCP resources and tools for Claude and other agents.
"""

from __future__ import annotations

# TODO: Implement MCP server when mcp package API stabilizes
# Will expose:
# - Resource: achub://content/{content_id} — fetch content docs
# - Tool: achub_search — search content
# - Tool: achub_check — run compliance checks
