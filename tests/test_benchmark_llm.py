"""Tests for benchmark LLM mode — prompt construction and response parsing."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure benchmarks module is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.runner import BenchmarkRunner, LLMResponseParser


def test_extract_json_from_code_block() -> None:
    text = 'Here is the result:\n```json\n{"should_execute": false, "violation": "pdt_rule"}\n```'
    result = LLMResponseParser.extract_json(text)
    assert result is not None
    assert result["should_execute"] is False
    assert result["violation"] == "pdt_rule"


def test_extract_json_bare() -> None:
    text = 'The answer is {"should_execute": false} based on rules.'
    result = LLMResponseParser.extract_json(text)
    assert result is not None
    assert result["should_execute"] is False


def test_extract_json_no_json() -> None:
    text = "There is no JSON here."
    result = LLMResponseParser.extract_json(text)
    assert result is None


def test_normalize_value() -> None:
    parser = LLMResponseParser()
    assert parser.normalize_value(True) == "true"
    assert parser.normalize_value("  Hello ") == "hello"
    assert parser.normalize_value(42) == "42"


def test_build_llm_prompt() -> None:
    runner = BenchmarkRunner(Path(__file__).resolve().parent.parent / "benchmarks")
    scenario = {
        "id": "test_scenario",
        "description": "Test scenario for PDT",
        "input": {"account_type": "margin", "equity": 20000},
        "expected": {"should_execute": False, "violation": "pdt_rule"},
    }
    context_docs = [
        {
            "metadata": {"title": "PDT Rule", "severity": "CRITICAL"},
            "body": "Do not make more than 3 day trades.",
        }
    ]
    system_prompt, user_prompt = runner.build_llm_prompt(scenario, context_docs)
    assert "PDT Rule" in system_prompt
    assert "CRITICAL" in system_prompt
    assert "should_execute" in user_prompt
    assert "margin" in user_prompt


def test_evaluate_response() -> None:
    runner = BenchmarkRunner(Path(__file__).resolve().parent.parent / "benchmarks")
    scenario = {
        "id": "test",
        "expected": {"should_execute": False, "violation": "pdt_rule"},
    }
    result = runner.evaluate(scenario, {"should_execute": False, "violation": "pdt_rule"})
    assert result.passed is True

    result = runner.evaluate(scenario, {"should_execute": True, "violation": "none"})
    assert result.passed is False
