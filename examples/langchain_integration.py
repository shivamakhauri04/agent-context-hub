"""LangChain integration example for agent-context-hub.

Shows how to wrap achub as LangChain tools that an agent can use to search
and retrieve curated knowledge content.

Requirements:
    pip install langchain langchain-openai agent-context-hub
"""
from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from achub.core.registry import ContentRegistry

# ---------------------------------------------------------------------------
# Tool definitions using LangChain's BaseTool interface
# ---------------------------------------------------------------------------

try:
    from langchain.tools import BaseTool
except ImportError:
    # Provide a stub so the file can be imported without langchain installed
    class BaseTool:  # type: ignore[no-redef]
        name: str = ""
        description: str = ""
        def _run(self, *args, **kwargs):  # noqa: ANN002, ANN003
            raise NotImplementedError


class AchubSearchTool(BaseTool):
    """LangChain tool that searches the achub content registry."""

    name: ClassVar[str] = "achub_search"
    description: ClassVar[str] = (
        "Search the agent-context-hub knowledge base for trading rules, "
        "regulations, and domain knowledge. Input should be a natural "
        "language query string."
    )

    _registry: ContentRegistry | None = None

    def _get_registry(self) -> ContentRegistry:
        if self._registry is None:
            self._registry = ContentRegistry(
                Path(__file__).resolve().parent.parent
            )
            self._registry.build()
        return self._registry

    def _run(self, query: str) -> str:
        registry = self._get_registry()
        results = registry.search(query)
        if not results:
            return "No relevant content found."
        lines: list[str] = []
        for result in results[:5]:
            content_id = result.get("content_id", "")
            title = result.get("metadata", {}).get("title", "")
            score = result.get("score", 0.0)
            lines.append(f"[{score:.3f}] {content_id} — {title}")
        return "\n".join(lines)


class AchubGetTool(BaseTool):
    """LangChain tool that fetches specific content by ID."""

    name: ClassVar[str] = "achub_get"
    description: ClassVar[str] = (
        "Retrieve a specific piece of content from agent-context-hub by its "
        "ID (e.g. 'trading/regulations/pdt-rule/rules'). Returns the full "
        "markdown body and metadata."
    )

    _registry: ContentRegistry | None = None

    def _get_registry(self) -> ContentRegistry:
        if self._registry is None:
            self._registry = ContentRegistry(
                Path(__file__).resolve().parent.parent
            )
            self._registry.build()
        return self._registry

    def _run(self, content_id: str) -> str:
        registry = self._get_registry()
        content = registry.get(content_id.strip())
        if content is None:
            return f"Content not found: {content_id}"
        title = content.get("metadata", {}).get("title", "Untitled")
        body = content.get("body", "")
        return f"# {title}\n\n{body}"


# ---------------------------------------------------------------------------
# Example usage pattern (commented out — requires a running LLM)
# ---------------------------------------------------------------------------
#
# from langchain_openai import ChatOpenAI
# from langchain.agents import initialize_agent, AgentType
#
# llm = ChatOpenAI(model="gpt-4o", temperature=0)
# tools = [AchubSearchTool(), AchubGetTool()]
#
# agent = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
# )
#
# response = agent.run(
#     "I have a margin account with $18,000 and I've made 3 day trades "
#     "this week. Can I make another day trade today?"
# )
# print(response)
