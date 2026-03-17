"""achub CLI — The missing knowledge layer for AI agents."""
from __future__ import annotations

import click

from achub import __version__
from achub.commands.annotate import annotate
from achub.commands.benchmark import benchmark
from achub.commands.check import check
from achub.commands.feedback import feedback
from achub.commands.get import get
from achub.commands.list import list_content
from achub.commands.prompt import prompt
from achub.commands.regime import regime
from achub.commands.search import search
from achub.commands.validate import validate
from achub.utils.paths import find_project_root


@click.group()
@click.version_option(version=__version__, prog_name="achub")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Enable debug logging.")
@click.pass_context
def main(ctx, verbose: bool):
    """achub — The missing knowledge layer for AI agents."""
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = find_project_root()
    if verbose:
        import logging

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(name)s %(levelname)s: %(message)s",
        )


# Register all commands
main.add_command(search)
main.add_command(get)
main.add_command(list_content, name="list")
main.add_command(validate)
main.add_command(check)
main.add_command(regime)
main.add_command(annotate)
main.add_command(feedback)
main.add_command(prompt)
main.add_command(benchmark)

# MCP command — lazy import, graceful if mcp not installed
try:
    from achub.commands.mcp_serve import mcp
    main.add_command(mcp)
except Exception:
    pass
