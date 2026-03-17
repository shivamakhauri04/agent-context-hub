"""Basic usage of agent-context-hub Python API."""
from __future__ import annotations

from pathlib import Path

from achub.core.registry import ContentRegistry


def main() -> None:
    # Initialize registry
    registry = ContentRegistry(Path(__file__).parent.parent)
    registry.build()

    # List all trading content
    print("=== Trading Content ===")
    for item in registry.list_all(domain="trading"):
        print(f"  {item['metadata']['id']}: {item['metadata']['title']}")

    # Search for relevant content
    print("\n=== Search: 'stock split adjustment' ===")
    results = registry.search("stock split adjustment")
    for result in results[:3]:
        content_id = result.get("content_id", "")
        score = result.get("score", 0.0)
        print(f"  [{score:.2f}] {content_id}")

    # Get specific content (handle None)
    content = registry.get("trading/regulations/pdt-rule/rules")
    if content is not None:
        print(f"\n## {content['metadata']['title']}")
        print(content["body"][:500])
    else:
        print("\nContent 'trading/regulations/pdt-rule/rules' not found.")


if __name__ == "__main__":
    main()
