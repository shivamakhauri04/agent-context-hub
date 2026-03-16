"""achub list — List available content."""
from __future__ import annotations

import click

from achub.core.registry import ContentRegistry
from achub.utils.formatting import print_content_list


@click.command("list")
@click.option("--domain", default=None, help="Filter by domain name.")
@click.option("--category", default=None, help="Filter by category name.")
@click.pass_context
def list_content(ctx, domain: str | None, category: str | None):
    """List all available content, optionally filtered by domain or category.

    Example: achub list --domain trading --category regulations
    """
    project_root = ctx.obj["project_root"]
    registry = ContentRegistry(project_root)
    registry.build()

    items = registry.list_all(domain=domain, category=category)

    if not items:
        click.echo("No content found.")
        return

    print_content_list(items)
