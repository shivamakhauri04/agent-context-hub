"""Tests for portfolio drift monitoring checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.portfolio_drift import check_portfolio_drift


def test_drift_no_allocations_skips() -> None:
    """No target_allocations -> skip."""
    portfolio = {"account_type": "margin", "equity": 50000}
    assert check_portfolio_drift(portfolio) == []


def test_drift_severe_critical() -> None:
    """Drift > 2x threshold -> CRITICAL."""
    portfolio = {
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 60, "current_pct": 80},
            {"asset_class": "bonds", "target_pct": 40, "current_pct": 20},
        ],
        "rebalance_threshold_pct": 5,
    }
    violations = check_portfolio_drift(portfolio)
    assert any("CRITICAL" in v and "us_equity" in v for v in violations)


def test_drift_exceeds_threshold_warning() -> None:
    """Drift > threshold but < 2x -> WARNING."""
    portfolio = {
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 60, "current_pct": 67},
            {"asset_class": "bonds", "target_pct": 40, "current_pct": 33},
        ],
        "rebalance_threshold_pct": 5,
    }
    violations = check_portfolio_drift(portfolio)
    assert any("WARNING" in v and "us_equity" in v for v in violations)


def test_drift_within_threshold_clean() -> None:
    """Drift within threshold -> no violations."""
    portfolio = {
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 60, "current_pct": 62},
            {"asset_class": "bonds", "target_pct": 40, "current_pct": 38},
        ],
        "rebalance_threshold_pct": 5,
    }
    assert check_portfolio_drift(portfolio) == []


def test_drift_allocations_dont_sum_to_100() -> None:
    """Target allocations sum deviates > 1% from 100 -> WARNING."""
    portfolio = {
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 50, "current_pct": 50},
            {"asset_class": "bonds", "target_pct": 30, "current_pct": 30},
        ],
        "rebalance_threshold_pct": 5,
    }
    violations = check_portfolio_drift(portfolio)
    assert any("WARNING" in v and "sum to" in v for v in violations)


def test_drift_allocations_sum_close_to_100_clean() -> None:
    """Target allocations sum within 1% of 100 -> no sum warning."""
    portfolio = {
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 60.5, "current_pct": 60.5},
            {"asset_class": "bonds", "target_pct": 39.8, "current_pct": 39.8},
        ],
        "rebalance_threshold_pct": 5,
    }
    violations = check_portfolio_drift(portfolio)
    assert not any("sum to" in v for v in violations)


def test_drift_stale_rebalance_warning() -> None:
    """Last rebalance > 90 days ago -> WARNING."""
    portfolio = {
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 60, "current_pct": 60},
            {"asset_class": "bonds", "target_pct": 40, "current_pct": 40},
        ],
        "rebalance_threshold_pct": 5,
        "last_rebalance_date": "2025-01-01",
    }
    violations = check_portfolio_drift(portfolio)
    assert any("WARNING" in v and "days ago" in v for v in violations)


def test_drift_no_current_pct_skips_drift_check() -> None:
    """Missing current_pct on allocation -> skip drift calc for that entry."""
    portfolio = {
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 60},
            {"asset_class": "bonds", "target_pct": 40, "current_pct": 40},
        ],
        "rebalance_threshold_pct": 5,
    }
    violations = check_portfolio_drift(portfolio)
    assert not any("us_equity" in v for v in violations)


def test_drift_checker_registered() -> None:
    """'portfolio-drift' should be in _RULE_CHECKERS."""
    assert "portfolio-drift" in _RULE_CHECKERS
    assert _RULE_CHECKERS["portfolio-drift"] is check_portfolio_drift
