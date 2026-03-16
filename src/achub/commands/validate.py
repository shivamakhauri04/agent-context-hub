"""achub validate — Validate content frontmatter against JSON schema."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from achub.core.domain import discover_domains, get_domain_path
from achub.core.schema import validate_content_file
from achub.utils.formatting import print_validation_results


@click.command()
@click.option(
    "--all", "validate_all", is_flag=True,
    help="Validate all content files across all domains.",
)
@click.argument("path", required=False, type=click.Path(exists=True))
@click.pass_context
def validate(ctx, validate_all: bool, path: str | None):
    """Validate frontmatter against the JSON schema.

    Provide a specific file path, or use --all to validate every content file.

    Example: achub validate domains/trading/regulations/pdt-rule.md
    Example: achub validate --all
    """
    project_root = ctx.obj["project_root"]
    has_errors = False

    if path:
        errors = validate_content_file(Path(path))
        print_validation_results(path, errors)
        if errors:
            has_errors = True
    elif validate_all:
        domains = discover_domains(project_root)
        if not domains:
            click.echo("No domains found.")
            return

        for domain in domains:
            domain_path = get_domain_path(project_root, domain)
            for md_file in sorted(domain_path.rglob("*.md")):
                if md_file.name == "DOMAIN.md":
                    continue
                errors = validate_content_file(md_file)
                print_validation_results(str(md_file), errors)
                if errors:
                    has_errors = True
    else:
        click.echo("Provide a file path or use --all to validate all content.", err=True)
        raise SystemExit(1)

    if has_errors:
        sys.exit(1)
