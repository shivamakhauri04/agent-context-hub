"""CrewAI integration example for agent-context-hub.

Shows how to wrap achub as CrewAI tools that an AI crew can use to access
curated domain knowledge during task execution.

Requirements:
    pip install crewai agent-context-hub
"""
from __future__ import annotations

from pathlib import Path

from achub.core.registry import ContentRegistry

# ---------------------------------------------------------------------------
# Registry singleton for tool functions
# ---------------------------------------------------------------------------

_registry: ContentRegistry | None = None


def _get_registry() -> ContentRegistry:
    global _registry  # noqa: PLW0603
    if _registry is None:
        _registry = ContentRegistry(Path(__file__).resolve().parent.parent)
        _registry.build()
    return _registry


# ---------------------------------------------------------------------------
# CrewAI tool definitions
# ---------------------------------------------------------------------------

try:
    from crewai.tools import tool
except ImportError:
    # Provide a stub decorator so the file can be imported without crewai
    def tool(func):  # type: ignore[no-redef]
        return func


@tool
def achub_search(query: str) -> str:
    """Search the agent-context-hub knowledge base for trading rules,
    regulations, and domain knowledge. Input should be a natural language
    query string.
    """
    registry = _get_registry()
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


@tool
def achub_get(content_id: str) -> str:
    """Retrieve a specific piece of content from agent-context-hub by its
    ID (e.g. 'trading/regulations/pdt-rule/rules'). Returns the full
    markdown body and metadata.
    """
    registry = _get_registry()
    content = registry.get(content_id.strip())
    if content is None:
        return f"Content not found: {content_id}"
    title = content.get("metadata", {}).get("title", "Untitled")
    body = content.get("body", "")
    return f"# {title}\n\n{body}"


# ---------------------------------------------------------------------------
# Example usage pattern (commented out — requires crewai and an LLM)
# ---------------------------------------------------------------------------
#
# from crewai import Agent, Task, Crew
#
# trading_analyst = Agent(
#     role="Trading Rule Analyst",
#     goal="Analyze trading portfolios for regulatory compliance",
#     backstory=(
#         "You are an expert in trading regulations like PDT rules, "
#         "wash sale rules, and market structure. You use the achub "
#         "knowledge base to look up precise rules before giving advice."
#     ),
#     tools=[achub_search, achub_get],
#     verbose=True,
# )
#
# compliance_check = Task(
#     description=(
#         "Review the following portfolio for any PDT or wash sale "
#         "violations. The account is a margin account with $18,000 "
#         "equity and 3 day trades this week. A TSLA position was sold "
#         "at a loss 15 days ago."
#     ),
#     expected_output="A compliance report listing any violations or warnings.",
#     agent=trading_analyst,
# )
#
# crew = Crew(
#     agents=[trading_analyst],
#     tasks=[compliance_check],
#     verbose=True,
# )
#
# result = crew.kickoff()
# print(result)

if __name__ == "__main__":
    try:
        import crewai  # noqa: F401
    except ImportError:
        print("CrewAI not installed. Run: pip install crewai")
        print("This example shows how to define achub tools for CrewAI agents.")
        raise SystemExit(1)

    # Quick test: verify tools work
    print("Search result:", achub_search("wash sale rule")[:200])
    print("Get result:", achub_get("trading/regulations/wash-sale/rules")[:200])
