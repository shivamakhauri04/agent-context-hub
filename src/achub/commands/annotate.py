"""achub annotate — Add notes to content items."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()


def _annotations_path(project_root: Path, content_id: str) -> Path:
    """Get the path to the annotations file for a given content ID."""
    safe_id = content_id.replace("/", "__")
    return project_root / ".achub" / "annotations" / f"{safe_id}.yaml"


def _load_annotations(path: Path) -> list[dict]:
    """Load existing annotations from a YAML file."""
    if not path.exists():
        return []
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, list) else []


def _save_annotations(path: Path, annotations: list[dict]) -> None:
    """Save annotations to a YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(annotations, f, default_flow_style=False, sort_keys=False)


@click.command()
@click.argument("content_id")
@click.option("--note", default=None, help="Annotation note to add.")
@click.pass_context
def annotate(ctx, content_id: str, note: str | None):
    """Add or view annotations on a content item.

    If --note is provided, appends it with a timestamp. Otherwise, shows existing annotations.

    Example: achub annotate trading/regulations/pdt-rule --note "Confirmed with broker"
    """
    project_root = ctx.obj["project_root"]
    ann_path = _annotations_path(project_root, content_id)

    if note:
        annotations = _load_annotations(ann_path)
        annotations.append({
            "note": note,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        _save_annotations(ann_path, annotations)
        console.print(f"[green]Annotation added to {content_id}[/green]")
    else:
        annotations = _load_annotations(ann_path)
        if not annotations:
            click.echo(f"No annotations for {content_id}.")
            return

        lines: list[str] = []
        for ann in annotations:
            ts = ann.get("timestamp", "unknown")
            text = ann.get("note", "")
            lines.append(f"[dim]{ts}[/dim]  {text}")

        console.print(
            Panel(
                "\n".join(lines),
                title=f"Annotations: {content_id}",
                border_style="cyan",
                expand=False,
            )
        )
