from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_content(content: dict) -> None:
    """Print a parsed content document with Rich formatting.

    Args:
        content: Parsed content dict with "metadata", "body", and "path" keys.
    """
    metadata = content.get("metadata", {})
    title = metadata.get("title", content.get("content_id", "Untitled"))
    body = content.get("body", "")

    # Metadata table
    if metadata:
        table = Table(title="Metadata", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="bold")
        table.add_column("Value")
        for key, value in metadata.items():
            table.add_row(str(key), str(value))
        console.print(table)

    # Body as markdown in a panel
    md = Markdown(body)
    panel = Panel(md, title=title, border_style="green", expand=False)
    console.print(panel)


def print_search_results(results: list) -> None:
    """Print search results as a Rich Table.

    Args:
        results: List of content dicts, each with a "score" key.
    """
    table = Table(title="Search Results", show_header=True, header_style="bold magenta")
    table.add_column("Rank", justify="right", style="bold")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Score", justify="right", style="green")

    for rank, item in enumerate(results, start=1):
        content_id = item.get("content_id", "")
        title = item.get("metadata", {}).get("title", "")
        score = item.get("score", 0.0)
        table.add_row(str(rank), content_id, title, f"{score:.4f}")

    console.print(table)


def print_content_list(items: list) -> None:
    """Print a list of content items as a Rich Table.

    Args:
        items: List of content dicts.
    """
    table = Table(title="Content", show_header=True, header_style="bold blue")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Domain", style="yellow")
    table.add_column("Category")

    for item in items:
        content_id = item.get("content_id", "")
        title = item.get("metadata", {}).get("title", "")
        domain = item.get("domain", "")
        category = item.get("category", "") or ""
        table.add_row(content_id, title, domain, category)

    console.print(table)


def print_validation_results(filepath: str, errors: list) -> None:
    """Print validation results with green check or red X.

    Args:
        filepath: Path to the validated file.
        errors: List of validation error strings.
    """
    if not errors:
        console.print(f"[bold green]PASS[/bold green] {filepath}")
    else:
        console.print(f"[bold red]FAIL[/bold red] {filepath}")
        for err in errors:
            console.print(f"  [red]- {err}[/red]")


def print_regime(regime: dict) -> None:
    """Print market regime info as a Rich Panel.

    Args:
        regime: Dict with regime information.
    """
    lines: list[str] = []
    for key, value in regime.items():
        lines.append(f"**{key}**: {value}")
    body = "\n".join(lines)
    md = Markdown(body)
    title = regime.get("name", regime.get("regime", "Market Regime"))
    panel = Panel(md, title=str(title), border_style="yellow", expand=False)
    console.print(panel)
