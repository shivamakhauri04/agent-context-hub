"""Tests for the structured check evaluator."""
from __future__ import annotations

from achub.core.checker import StructuredCheckEvaluator


def test_simple_comparison() -> None:
    evaluator = StructuredCheckEvaluator()
    checks = [
        {"id": "test1", "condition": "x > 5", "severity": "high", "message": "x too low"},
    ]
    results = evaluator.evaluate_checks(checks, {"x": 10})
    assert results[0].passed is True

    results = evaluator.evaluate_checks(checks, {"x": 3})
    assert results[0].passed is False


def test_equality_string() -> None:
    evaluator = StructuredCheckEvaluator()
    checks = [
        {
            "id": "test1",
            "condition": "account_type == 'cash'",
            "severity": "low",
            "message": "Not cash",
        },
    ]
    results = evaluator.evaluate_checks(checks, {"account_type": "cash"})
    assert results[0].passed is True

    results = evaluator.evaluate_checks(checks, {"account_type": "margin"})
    assert results[0].passed is False


def test_or_condition() -> None:
    evaluator = StructuredCheckEvaluator()
    checks = [
        {
            "id": "pdt",
            "condition": "day_trades_count_5d < 4 OR account_type == 'cash' OR equity >= 25000",
            "severity": "critical",
            "message": "PDT violation",
        },
    ]
    # Should pass: cash account
    results = evaluator.evaluate_checks(
        checks, {"day_trades_count_5d": 5, "account_type": "cash", "equity": 10000}
    )
    assert results[0].passed is True

    # Should pass: high equity
    results = evaluator.evaluate_checks(
        checks, {"day_trades_count_5d": 5, "account_type": "margin", "equity": 30000}
    )
    assert results[0].passed is True

    # Should fail: margin, low equity, 4+ day trades
    results = evaluator.evaluate_checks(
        checks, {"day_trades_count_5d": 4, "account_type": "margin", "equity": 15000}
    )
    assert results[0].passed is False


def test_and_condition() -> None:
    evaluator = StructuredCheckEvaluator()
    checks = [
        {"id": "test1", "condition": "x > 5 AND y < 10", "severity": "medium", "message": "fail"},
    ]
    results = evaluator.evaluate_checks(checks, {"x": 6, "y": 9})
    assert results[0].passed is True

    results = evaluator.evaluate_checks(checks, {"x": 6, "y": 11})
    assert results[0].passed is False


def test_not_condition() -> None:
    evaluator = StructuredCheckEvaluator()
    checks = [
        {
            "id": "test1",
            "condition": "NOT is_blocked == 'true'",
            "severity": "low",
            "message": "blocked",
        },
    ]
    results = evaluator.evaluate_checks(checks, {"is_blocked": "false"})
    assert results[0].passed is True


def test_missing_variable() -> None:
    evaluator = StructuredCheckEvaluator()
    checks = [
        {"id": "test1", "condition": "missing_var > 5", "severity": "low", "message": "fail"},
    ]
    results = evaluator.evaluate_checks(checks, {})
    assert results[0].passed is False


def test_nested_parentheses() -> None:
    evaluator = StructuredCheckEvaluator()
    checks = [
        {
            "id": "test1",
            "condition": "(x > 5 OR y > 5) AND z == 'ok'",
            "severity": "low",
            "message": "fail",
        },
    ]
    results = evaluator.evaluate_checks(checks, {"x": 3, "y": 6, "z": "ok"})
    assert results[0].passed is True

    results = evaluator.evaluate_checks(checks, {"x": 3, "y": 6, "z": "bad"})
    assert results[0].passed is False
