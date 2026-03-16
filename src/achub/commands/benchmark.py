"""achub benchmark — Run benchmark scenarios against domains."""
from __future__ import annotations

import json
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

console = Console()


def _load_suite(project_root: Path, domain: str) -> dict | None:
    """Load the benchmark suite.yaml for a domain."""
    suite_path = project_root / "benchmarks" / "domains" / domain / "suite.yaml"
    if not suite_path.exists():
        return None
    with open(suite_path) as f:
        return yaml.safe_load(f)


def _run_scenario_against_endpoint(scenario: dict, endpoint: str) -> dict:
    """POST a scenario to an endpoint and return the response."""
    import urllib.error
    import urllib.request

    payload = json.dumps(scenario).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "body": json.loads(body) if body else {},
            }
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": {}, "error": str(e)}
    except Exception as e:
        return {"status": 0, "body": {}, "error": str(e)}


def _evaluate_response(scenario: dict, response: dict) -> dict:
    """Evaluate a response against expected outputs in the scenario."""
    expected = scenario.get("expected", {})
    actual_body = response.get("body", {})
    passed = True
    details: list[str] = []

    for key, expected_value in expected.items():
        actual_value = actual_body.get(key)
        if actual_value != expected_value:
            passed = False
            details.append(f"{key}: expected={expected_value!r}, got={actual_value!r}")
        else:
            details.append(f"{key}: OK")

    return {"passed": passed, "details": details}


@click.group()
@click.pass_context
def benchmark(ctx):
    """Benchmark commands for testing domain knowledge."""
    pass


@benchmark.command()
@click.option("--domain", required=True, help="Domain to benchmark (e.g. trading).")
@click.option("--scenario", "scenario_name", default=None, help="Run a specific scenario by name.")
@click.option("--endpoint", default=None, help="URL to POST scenarios to for evaluation.")
@click.pass_context
def run(ctx, domain: str, scenario_name: str | None, endpoint: str | None):
    """Run benchmark scenarios for a domain.

    Loads scenarios from benchmarks/domains/{domain}/suite.yaml. If --endpoint is
    provided, POSTs each scenario and evaluates the response. Otherwise, performs
    a dry run showing scenario details.

    Example: achub benchmark run --domain trading --scenario pdt-basic
    Example: achub benchmark run --domain trading --endpoint http://localhost:8000/check
    """
    project_root = ctx.obj["project_root"]
    suite = _load_suite(project_root, domain)

    if suite is None:
        click.echo(f"No benchmark suite found for domain: {domain}", err=True)
        raise SystemExit(1)

    scenarios = suite.get("scenarios", [])
    if not scenarios:
        click.echo("No scenarios defined in suite.", err=True)
        raise SystemExit(1)

    if scenario_name:
        scenarios = [s for s in scenarios if s.get("name") == scenario_name]
        if not scenarios:
            click.echo(f"Scenario not found: {scenario_name}", err=True)
            raise SystemExit(1)

    if endpoint:
        _run_with_endpoint(scenarios, endpoint, domain)
    else:
        _dry_run(scenarios, domain)


def _dry_run(scenarios: list[dict], domain: str) -> None:
    """Display scenario details without running them."""
    table = Table(
        title=f"Benchmark Scenarios ({domain}) — Dry Run",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Input Keys")
    table.add_column("Expected Keys")

    for scenario in scenarios:
        name = scenario.get("name", "unnamed")
        desc = scenario.get("description", "")
        raw_input = scenario.get("input", {})
        input_keys = ", ".join(raw_input.keys()) if isinstance(raw_input, dict) else ""
        raw_expected = scenario.get("expected", {})
        expected_keys = ", ".join(raw_expected.keys()) if isinstance(raw_expected, dict) else ""
        table.add_row(name, desc, input_keys, expected_keys)

    console.print(table)
    console.print(f"\n[dim]Total: {len(scenarios)} scenario(s). Use --endpoint to run them.[/dim]")


def _run_with_endpoint(scenarios: list[dict], endpoint: str, domain: str) -> None:
    """Run scenarios against an endpoint and display results."""
    results_table = Table(
        title=f"Benchmark Results ({domain})",
        show_header=True,
        header_style="bold magenta",
    )
    results_table.add_column("Scenario", style="cyan")
    results_table.add_column("Status")
    results_table.add_column("Result")
    results_table.add_column("Details")

    passed_count = 0
    total = len(scenarios)

    for scenario in scenarios:
        name = scenario.get("name", "unnamed")
        response = _run_scenario_against_endpoint(scenario.get("input", {}), endpoint)

        if "error" in response:
            results_table.add_row(
                name,
                f"[red]{response['status']}[/red]",
                "[red]ERROR[/red]",
                response["error"],
            )
            continue

        evaluation = _evaluate_response(scenario, response)
        if evaluation["passed"]:
            passed_count += 1
            status_str = "[green]PASS[/green]"
        else:
            status_str = "[red]FAIL[/red]"

        details = "; ".join(evaluation["details"])
        results_table.add_row(name, str(response["status"]), status_str, details)

    console.print(results_table)
    console.print(f"\n[bold]{passed_count}/{total} scenarios passed.[/bold]")
