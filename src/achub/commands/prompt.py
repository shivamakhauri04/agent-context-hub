"""achub prompt — Generate system prompts for agent integration."""
from __future__ import annotations

import click

from achub.core.registry import ContentRegistry
from achub.prompts import get_system_prompt


@click.command()
@click.option(
    "--domain",
    required=True,
    help="Domain to generate prompt for (e.g. trading).",
)
@click.pass_context
def prompt(ctx, domain: str):
    """Generate a system prompt with mandatory achub check instructions.

    Outputs a prompt snippet that tells agents WHEN and WHY to call achub tools.

    Example: achub prompt --domain trading
    """
    project_root = ctx.obj["project_root"]
    registry = ContentRegistry(project_root)
    registry.build()

    output = get_system_prompt(domain, registry)
    click.echo(output)
