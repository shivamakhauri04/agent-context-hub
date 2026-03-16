"""achub search — Full-text search across all content."""
from __future__ import annotations

import click

from achub.core.registry import ContentRegistry
from achub.utils.formatting import print_search_results


@click.command()
@click.argument("query")
@click.option("--domain", default=None, help="Filter results to a specific domain.")
@click.option("--limit", default=10, show_default=True, help="Maximum number of results to return.")
@click.pass_context
def search(ctx, query: str, domain: str | None, limit: int):
    """Search content by query string.

    Uses TF-IDF indexing across all domains to find relevant content.

    Example: achub search "stock split" --domain trading --limit 5
    """
    project_root = ctx.obj["project_root"]
    registry = ContentRegistry(project_root)
    registry.build()

    results = registry.search(query, domain=domain)
    results = results[:limit]

    if not results:
        click.echo("No results found.")
        return

    print_search_results(results)
