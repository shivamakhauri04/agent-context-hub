"""Domain-agnostic benchmark evaluator and scorer for agent-context-hub."""
from __future__ import annotations

from benchmarks.runner import ScenarioResult


def score_results(results: list[ScenarioResult]) -> dict:
    """Score a list of scenario results.

    Returns a dict with total, passed, failed, score_pct, and details.
    """
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    score_pct = round((passed / total) * 100, 1) if total > 0 else 0.0

    details = []
    for r in results:
        details.append({
            "scenario_id": r.scenario_id,
            "passed": r.passed,
            "details": r.details,
        })

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "score_pct": score_pct,
        "details": details,
    }


def format_report(score: dict) -> str:
    """Format a score dict into a human-readable text report."""
    lines = [
        "=" * 50,
        "BENCHMARK REPORT",
        "=" * 50,
        f"Total scenarios : {score['total']}",
        f"Passed          : {score['passed']}",
        f"Failed          : {score['failed']}",
        f"Score           : {score['score_pct']}%",
        "-" * 50,
    ]

    for entry in score["details"]:
        status = "PASS" if entry["passed"] else "FAIL"
        lines.append(f"[{status}] {entry['scenario_id']}")
        if entry["details"]:
            for detail_line in entry["details"].split("\n"):
                lines.append(f"       {detail_line}")

    lines.append("=" * 50)
    return "\n".join(lines)


def generate_badge_url(score: dict) -> str:
    """Generate a shields.io badge URL based on the score."""
    passed = score["passed"]
    total = score["total"]
    pct = score["score_pct"]

    if pct >= 100:
        color = "brightgreen"
    elif pct >= 60:
        color = "yellow"
    else:
        color = "red"

    label = "achub--benchmark"
    message = f"{passed}%2F{total}%20passed"

    return f"https://img.shields.io/badge/{label}-{message}-{color}"
