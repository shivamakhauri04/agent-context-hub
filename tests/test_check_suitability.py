"""Tests for suitability checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.suitability import check_suitability


def test_suitability_risk_mismatch_critical() -> None:
    """Strategy risk_level=5 vs customer_risk_tolerance=2 -> CRITICAL."""
    portfolio = {
        "customer_risk_tolerance": 2,
        "customer_experience_level": 5,
        "pending_strategies": [
            {"strategy": "naked_put", "symbol": "TSLA", "risk_level": 5, "complexity": 3},
        ],
        "turnover_ratio_annual": 1.0,
        "cost_equity_ratio_annual": 0.05,
        "positions": [],
        "equity": 50000,
    }
    violations = check_suitability(portfolio)
    assert any("CRITICAL" in v and "risk" in v.lower() for v in violations)


def test_suitability_experience_mismatch_warning() -> None:
    """Strategy complexity=4 vs customer_experience_level=2 -> WARNING."""
    portfolio = {
        "customer_risk_tolerance": 5,
        "customer_experience_level": 2,
        "pending_strategies": [
            {"strategy": "iron_condor", "symbol": "SPY", "risk_level": 3, "complexity": 4},
        ],
        "turnover_ratio_annual": 1.0,
        "cost_equity_ratio_annual": 0.05,
        "positions": [],
        "equity": 50000,
    }
    violations = check_suitability(portfolio)
    assert any("WARNING" in v and "experience" in v.lower() for v in violations)


def test_suitability_churning_critical() -> None:
    """Turnover ratio 8.5 -> CRITICAL (excessive trading / churning)."""
    portfolio = {
        "customer_risk_tolerance": 5,
        "customer_experience_level": 5,
        "pending_strategies": [],
        "turnover_ratio_annual": 8.5,
        "cost_equity_ratio_annual": 0.05,
        "positions": [],
        "equity": 50000,
    }
    violations = check_suitability(portfolio)
    assert any("CRITICAL" in v and "turnover" in v.lower() for v in violations)


def test_suitability_high_cost_warning() -> None:
    """Cost-equity ratio 0.25 -> WARNING (excessive costs)."""
    portfolio = {
        "customer_risk_tolerance": 5,
        "customer_experience_level": 5,
        "pending_strategies": [],
        "turnover_ratio_annual": 1.0,
        "cost_equity_ratio_annual": 0.25,
        "positions": [],
        "equity": 50000,
    }
    violations = check_suitability(portfolio)
    assert any("WARNING" in v and "cost" in v.lower() for v in violations)


def test_suitability_concentration_warning() -> None:
    """Single position AAPL at 30% of portfolio -> WARNING."""
    portfolio = {
        "customer_risk_tolerance": 5,
        "customer_experience_level": 5,
        "pending_strategies": [],
        "turnover_ratio_annual": 1.0,
        "cost_equity_ratio_annual": 0.05,
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 100,
                "avg_cost": 150.00,
                "current_price": 150.00,
                "unrealized_pnl": 0,
            },
        ],
        "equity": 50000,
    }
    violations = check_suitability(portfolio)
    assert any("WARNING" in v and "concentration" in v.lower() for v in violations)


def test_suitability_missing_profile_critical() -> None:
    """Pending strategies but no customer_risk_tolerance -> CRITICAL."""
    portfolio = {
        "customer_experience_level": 3,
        "pending_strategies": [
            {"strategy": "covered_call", "symbol": "AAPL", "risk_level": 2, "complexity": 2},
        ],
        "turnover_ratio_annual": 1.0,
        "cost_equity_ratio_annual": 0.05,
        "positions": [],
        "equity": 50000,
    }
    violations = check_suitability(portfolio)
    assert any("CRITICAL" in v and "profile" in v.lower() for v in violations)


def test_suitability_within_limits_passes() -> None:
    """All metrics within acceptable limits -> no violations."""
    portfolio = {
        "customer_risk_tolerance": 4,
        "customer_experience_level": 4,
        "pending_strategies": [
            {"strategy": "covered_call", "symbol": "AAPL", "risk_level": 2, "complexity": 2},
        ],
        "turnover_ratio_annual": 2.0,
        "cost_equity_ratio_annual": 0.05,
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "avg_cost": 150.00,
                "current_price": 150.00,
                "unrealized_pnl": 0,
            },
        ],
        "equity": 50000,
    }
    violations = check_suitability(portfolio)
    assert violations == []


def test_suitability_checker_registered() -> None:
    """'suitability' should be in _RULE_CHECKERS."""
    assert "suitability" in _RULE_CHECKERS
    assert _RULE_CHECKERS["suitability"] is check_suitability
