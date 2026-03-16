"""achub get — Retrieve content by ID."""
from __future__ import annotations

import json

import click

from achub.core.registry import ContentRegistry
from achub.utils.formatting import print_content


@click.command()
@click.argument("content_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "json", "llm"]),
    default="markdown",
    show_default=True,
    help="Output format: markdown (rich), json (structured), or llm (token-efficient).",
)
@click.pass_context
def get(ctx, content_id: str, output_format: str):
    """Get content by its ID.

    Retrieves a specific piece of content and renders it in the requested format.

    Example: achub get trading/regulations/pdt-rule --format llm
    """
    project_root = ctx.obj["project_root"]
    registry = ContentRegistry(project_root)
    registry.build()

    content = registry.get(content_id)
    if content is None:
        click.echo(f"Content not found: {content_id}", err=True)
        raise SystemExit(1)

    if output_format == "markdown":
        print_content(content)
    elif output_format == "json":
        output = {
            "content_id": content.get("content_id"),
            "metadata": content.get("metadata", {}),
            "body": content.get("body", ""),
        }
        click.echo(json.dumps(output, indent=2))
    elif output_format == "llm":
        _print_llm_format(content)


def _print_llm_format(content: dict) -> None:
    """Print token-efficient output: title, rules/checklist sections only."""
    metadata = content.get("metadata", {})
    title = metadata.get("title", content.get("content_id", "Untitled"))
    click.echo(f"# {title}")

    body = content.get("body", "")
    # Extract only rules, checklist, and key sections — skip verbose prose
    in_relevant_section = False
    for line in body.splitlines():
        stripped = line.strip().lower()
        # Detect section headers that contain useful info
        if line.startswith("#"):
            is_relevant = any(
                kw in stripped
                for kw in [
                    "rule", "checklist", "requirement",
                    "key point", "warning", "constraint", "limit",
                ]
            )
            if is_relevant:
                in_relevant_section = True
                click.echo(line)
            else:
                in_relevant_section = False
        elif in_relevant_section:
            # Print non-empty lines in relevant sections
            if line.strip():
                click.echo(line)
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            # Always include bullet points as they tend to be actionable
            click.echo(line)
