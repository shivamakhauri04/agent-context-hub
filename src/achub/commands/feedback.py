"""achub feedback — Rate and comment on content items."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click
import yaml
from rich.console import Console

console = Console()


def _feedback_path(project_root: Path, content_id: str) -> Path:
    """Get the path to the feedback file for a given content ID."""
    safe_id = content_id.replace("/", "__")
    return project_root / ".achub" / "feedback" / f"{safe_id}.yaml"


def _load_feedback(path: Path) -> list[dict]:
    """Load existing feedback from a YAML file."""
    if not path.exists():
        return []
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, list) else []


def _save_feedback(path: Path, entries: list[dict]) -> None:
    """Save feedback to a YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(entries, f, default_flow_style=False, sort_keys=False)


@click.command()
@click.argument("content_id")
@click.option(
    "--rating",
    required=True,
    type=click.Choice(["up", "down"]),
    help="Thumbs up or down rating.",
)
@click.option("--comment", default=None, help="Optional comment with your feedback.")
@click.pass_context
def feedback(ctx, content_id: str, rating: str, comment: str | None):
    """Submit feedback on a content item.

    Appends a rating (up/down) with optional comment and timestamp.

    Example: achub feedback trading/regulations/pdt-rule --rating up --comment "Very clear"
    """
    project_root = ctx.obj["project_root"]
    fb_path = _feedback_path(project_root, content_id)

    entries = _load_feedback(fb_path)

    entry: dict = {
        "rating": rating,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if comment:
        entry["comment"] = comment

    entries.append(entry)
    _save_feedback(fb_path, entries)

    icon = "[green]thumbs up[/green]" if rating == "up" else "[red]thumbs down[/red]"
    console.print(f"Feedback recorded for {content_id}: {icon}")
