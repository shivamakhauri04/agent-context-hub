"""achub search — Full-text search across all content."""
from __future__ import annotations

import json

import click

from achub.core.registry import ContentRegistry
from achub.utils.formatting import print_search_results


@click.command()
@click.argument("query")
@click.option("--domain", default=None, help="Filter results to a specific domain.")
@click.option("--limit", default=10, show_default=True, help="Maximum number of results to return.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    show_default=True,
    help="Output format.",
)
@click.pass_context
def search(ctx, query: str, domain: str | None, limit: int, output_format: str):
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
        if output_format == "json":
            click.echo(json.dumps({"results": []}))
        else:
            click.echo("No results found.")
        return

    if output_format == "json":
        output = []
        for item in results:
            output.append({
                "content_id": item.get("content_id", ""),
                "title": item.get("metadata", {}).get("title", ""),
                "score": round(item.get("score", 0.0), 4),
                "severity": item.get("metadata", {}).get("severity", ""),
                "domain": item.get("domain", ""),
            })
        click.echo(json.dumps({"results": output}))
    else:
        print_search_results(results)
