"""Benchmark runner for agent-context-hub."""
from __future__ import annotations
import json
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool
    expected: dict
    actual: dict | None
    details: str


class BenchmarkRunner:
    def __init__(self, benchmarks_dir: Path):
        self.benchmarks_dir = benchmarks_dir

    def load_suite(self, domain: str) -> dict:
        suite_path = self.benchmarks_dir / "domains" / domain / "suite.yaml"
        with open(suite_path) as f:
            return yaml.safe_load(f)

    def load_scenario(self, domain: str, scenario_name: str) -> dict:
        path = self.benchmarks_dir / "domains" / domain / "scenarios" / f"{scenario_name}.yaml"
        with open(path) as f:
            return yaml.safe_load(f)

    def run_scenario(self, scenario: dict, agent_response: dict | None = None) -> ScenarioResult:
        """Run a single scenario. If agent_response is None, returns a dry-run result."""
        if agent_response is None:
            return ScenarioResult(
                scenario_id=scenario["id"],
                passed=False,
                expected=scenario["expected"],
                actual=None,
                details="Dry run — no agent response provided"
            )
        return self.evaluate(scenario, agent_response)

    def evaluate(self, scenario: dict, response: dict) -> ScenarioResult:
        """Evaluate agent response against expected behavior."""
        checks = scenario["expected"]
        passed = True
        details = []

        for check_key, expected_value in checks.items():
            actual = response.get(check_key)
            if actual != expected_value:
                passed = False
                details.append(f"FAIL: {check_key} expected={expected_value}, got={actual}")
            else:
                details.append(f"PASS: {check_key}")

        return ScenarioResult(
            scenario_id=scenario["id"],
            passed=passed,
            expected=checks,
            actual=response,
            details="\n".join(details)
        )

    def run_suite(self, domain: str, agent_responses: dict[str, dict] | None = None) -> list[ScenarioResult]:
        suite = self.load_suite(domain)
        results = []
        for scenario_ref in suite["scenarios"]:
            scenario = self.load_scenario(domain, scenario_ref["file"].replace(".yaml", ""))
            agent_resp = (agent_responses or {}).get(scenario["id"])
            results.append(self.run_scenario(scenario, agent_resp))
        return results
