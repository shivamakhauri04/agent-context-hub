"""Benchmark runner for agent-context-hub."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool
    expected: dict
    actual: dict | None
    details: str


class LLMResponseParser:
    """Extract JSON from LLM responses, handling markdown code blocks."""

    @staticmethod
    def extract_json(text: str) -> dict | None:
        """Extract JSON from text, handling ```json blocks and bare JSON."""
        # Try markdown code block first
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        # Try bare JSON
        for start in range(len(text)):
            if text[start] == "{":
                for end in range(len(text), start, -1):
                    if text[end - 1] == "}":
                        try:
                            return json.loads(text[start:end])
                        except json.JSONDecodeError:
                            continue
        return None

    @staticmethod
    def normalize_value(value) -> str:
        """Normalize a value for fuzzy matching."""
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, str):
            return value.strip().lower()
        return str(value).lower()


class BenchmarkRunner:
    def __init__(self, benchmarks_dir: Path):
        self.benchmarks_dir = benchmarks_dir

    def load_suite(self, domain: str) -> dict:
        suite_path = self.benchmarks_dir / "domains" / domain / "suite.yaml"
        with open(suite_path) as f:
            return yaml.safe_load(f)

    def load_scenario(self, domain: str, scenario_name: str) -> dict:
        path = (
            self.benchmarks_dir / "domains" / domain / "scenarios" / f"{scenario_name}.yaml"
        )
        with open(path) as f:
            return yaml.safe_load(f)

    def run_scenario(
        self, scenario: dict, agent_response: dict | None = None
    ) -> ScenarioResult:
        """Run a single scenario. If agent_response is None, returns a dry-run result."""
        if agent_response is None:
            return ScenarioResult(
                scenario_id=scenario["id"],
                passed=False,
                expected=scenario["expected"],
                actual=None,
                details="Dry run — no agent response provided",
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
                details.append(
                    f"FAIL: {check_key} expected={expected_value}, got={actual}"
                )
            else:
                details.append(f"PASS: {check_key}")

        return ScenarioResult(
            scenario_id=scenario["id"],
            passed=passed,
            expected=checks,
            actual=response,
            details="\n".join(details),
        )

    def run_suite(
        self, domain: str, agent_responses: dict[str, dict] | None = None
    ) -> list[ScenarioResult]:
        suite = self.load_suite(domain)
        results = []
        for scenario_ref in suite["scenarios"]:
            scenario = self.load_scenario(
                domain, scenario_ref["file"].replace(".yaml", "")
            )
            agent_resp = (agent_responses or {}).get(scenario["id"])
            results.append(self.run_scenario(scenario, agent_resp))
        return results

    def build_llm_prompt(
        self, scenario: dict, context_content: list[dict]
    ) -> tuple[str, str]:
        """Build system and user prompts for LLM evaluation.

        Args:
            scenario: The benchmark scenario dict.
            context_content: List of content dicts from ContentRegistry.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        context_blocks = []
        for doc in context_content:
            meta = doc.get("metadata", {})
            context_blocks.append(
                f"--- {meta.get('title', 'Untitled')} "
                f"(severity: {meta.get('severity', 'unknown')}) ---\n"
                f"{doc.get('body', '')}"
            )

        context_text = "\n\n".join(context_blocks)
        expected_keys = list(scenario.get("expected", {}).keys())

        system_prompt = (
            "You are an expert trading agent evaluator. Given domain knowledge "
            "and a trading scenario, analyze the situation and respond with a JSON "
            "object.\n\n"
            f"Domain knowledge:\n{context_text}"
        )

        user_prompt = (
            f"Scenario: {scenario.get('description', '')}\n\n"
            f"Input: {json.dumps(scenario.get('input', {}), indent=2)}\n\n"
            f"Respond with a JSON object containing these keys: {expected_keys}\n"
            "Use the domain knowledge above to determine the correct values."
        )

        return system_prompt, user_prompt

    def run_scenario_with_llm(
        self,
        scenario: dict,
        context_content: list[dict],
        api_base: str,
        model: str,
    ) -> ScenarioResult:
        """Run a scenario by querying an LLM and evaluating the response."""
        try:
            import httpx
        except ImportError:
            return ScenarioResult(
                scenario_id=scenario["id"],
                passed=False,
                expected=scenario.get("expected", {}),
                actual=None,
                details="httpx not installed. Run: pip install agent-context-hub[benchmark]",
            )

        system_prompt, user_prompt = self.build_llm_prompt(scenario, context_content)

        payload = {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            url = f"{api_base.rstrip('/')}/chat/completions"
            resp = httpx.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
        except Exception as e:
            return ScenarioResult(
                scenario_id=scenario["id"],
                passed=False,
                expected=scenario.get("expected", {}),
                actual=None,
                details=f"LLM request failed: {e}",
            )

        parser = LLMResponseParser()
        parsed = parser.extract_json(content)
        if parsed is None:
            return ScenarioResult(
                scenario_id=scenario["id"],
                passed=False,
                expected=scenario.get("expected", {}),
                actual=None,
                details=f"Could not parse JSON from LLM response: {content[:200]}",
            )

        return self.evaluate(scenario, parsed)
