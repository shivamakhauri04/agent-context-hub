"""Basic usage of agent-context-hub Python API."""
from __future__ import annotations

from pathlib import Path

from achub.core.registry import ContentRegistry
from achub.prompts import get_system_prompt


def main() -> None:
    # Initialize registry
    registry = ContentRegistry(Path(__file__).parent.parent)
    registry.build()

    # List all trading content
    print("=== Trading Content ===")
    for item in registry.list_all(domain="trading"):
        print(f"  {item['content_id']}: {item['metadata']['title']}")

    # Search for relevant content
    print("\n=== Search: 'stock split adjustment' ===")
    results = registry.search("stock split adjustment")
    for result in results[:3]:
        content_id = result.get("content_id", "")
        score = result.get("score", 0.0)
        stale_marker = " [STALE]" if result.get("stale") else ""
        print(f"  [{score:.2f}] {content_id}{stale_marker}")

    # Get specific content (handle None)
    content = registry.get("trading/regulations/pdt-rule/rules")
    if content is not None:
        print(f"\n## {content['metadata']['title']}")
        if content.get("stale"):
            print(f"  WARNING: Content is stale ({content['stale_days']} days old)")
        print(content["body"][:500])
    else:
        print("\nContent 'trading/regulations/pdt-rule/rules' not found.")

    # Generate system prompt for agents
    print("\n=== System Prompt (trading) ===")
    prompt = get_system_prompt("trading", registry)
    print(prompt[:500])


if __name__ == "__main__":
    main()
