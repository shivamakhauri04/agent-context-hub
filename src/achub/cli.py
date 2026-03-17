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
from achub.commands.regime import regime
from achub.commands.search import search
from achub.commands.validate import validate


@click.group()
@click.version_option(version=__version__, prog_name="achub")
@click.pass_context
def main(ctx):
    """achub — The missing knowledge layer for AI agents."""
    ctx.ensure_object(dict)
    # Store project root in context for commands to use
    ctx.obj["project_root"] = _find_project_root()


def _find_project_root():
    from pathlib import Path

    path = Path(__file__).resolve().parent
    while path != path.parent:
        if (path / "pyproject.toml").exists():
            return path
        path = path.parent
    return Path.cwd()


# Register all commands
main.add_command(search)
main.add_command(get)
main.add_command(list_content, name="list")
main.add_command(validate)
main.add_command(check)
main.add_command(regime)
main.add_command(annotate)
main.add_command(feedback)
main.add_command(benchmark)

# MCP command — lazy import, graceful if mcp not installed
try:
    from achub.commands.mcp_serve import mcp
    main.add_command(mcp)
except Exception:
    pass
