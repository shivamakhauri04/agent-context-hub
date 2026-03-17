"""achub mcp — MCP server commands."""
from __future__ import annotations

import click


@click.group()
def mcp():
    """MCP server commands for agent integration."""
    pass


@mcp.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    show_default=True,
    help="Transport protocol for the MCP server.",
)
def serve(transport: str):
    """Start the MCP server.

    Exposes achub content as MCP tools for Claude and other agents.

    Requires: pip install agent-context-hub[mcp]

    Example: achub mcp serve --transport stdio
    """
    try:
        from achub.integrations.mcp import run_server
    except ImportError:
        click.echo(
            "MCP dependencies not installed. Run:\n"
            "  pip install agent-context-hub[mcp]",
            err=True,
        )
        raise SystemExit(1)

    click.echo(f"Starting MCP server (transport={transport})...", err=True)
    run_server(transport=transport)
