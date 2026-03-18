"""Tests for goal-based allocation checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.goal_allocation import check_goal_allocation


def test_goal_equity_too_high_short_horizon() -> None:
    """2yr horizon with 60% equity -> WARNING."""
    portfolio = {
        "goal_type": "house_down_payment",
        "goal_time_horizon_years": 2,
        "goal_equity_pct": 60,
        "goal_bond_pct": 20,
        "goal_cash_pct": 20,
        "customer_risk_score": 5,
    }
    violations = check_goal_allocation(portfolio)
    assert any("WARNING" in v and "equity" in v.lower() for v in violations)


def test_goal_emergency_fund_in_equities() -> None:
    """Emergency fund with 20% equity -> CRITICAL."""
    portfolio = {
        "goal_type": "emergency_fund",
        "goal_equity_pct": 20,
        "goal_bond_pct": 30,
        "goal_cash_pct": 50,
        "customer_risk_score": 3,
    }
    violations = check_goal_allocation(portfolio)
    assert any("CRITICAL" in v and "emergency" in v.lower() for v in violations)


def test_goal_emergency_fund_all_cash_passes() -> None:
    """Emergency fund with 0% equity -> no violations."""
    portfolio = {
        "goal_type": "emergency_fund",
        "goal_equity_pct": 0,
        "goal_bond_pct": 10,
        "goal_cash_pct": 90,
        "customer_risk_score": 1,
    }
    violations = check_goal_allocation(portfolio)
    assert violations == []


def test_goal_risk_mismatch_warning() -> None:
    """Low risk score with high equity allocation -> WARNING."""
    portfolio = {
        "goal_type": "retirement",
        "goal_time_horizon_years": 25,
        "goal_equity_pct": 80,
        "goal_bond_pct": 15,
        "goal_cash_pct": 5,
        "customer_risk_score": 2,
    }
    violations = check_goal_allocation(portfolio)
    assert any("WARNING" in v and "risk" in v.lower() for v in violations)


def test_goal_missing_risk_score() -> None:
    """Goal type set but no customer_risk_score -> WARNING."""
    portfolio = {
        "goal_type": "house_down_payment",
        "goal_time_horizon_years": 3,
        "goal_equity_pct": 40,
        "goal_bond_pct": 30,
        "goal_cash_pct": 30,
    }
    violations = check_goal_allocation(portfolio)
    assert any("WARNING" in v and "risk" in v.lower() for v in violations)


def test_goal_no_goal_type_skips() -> None:
    """No goal_type -> empty list."""
    portfolio = {
        "equity": 50000,
        "cash": 10000,
    }
    violations = check_goal_allocation(portfolio)
    assert violations == []


def test_goal_checker_registered() -> None:
    """'goal-allocation' should be in _RULE_CHECKERS."""
    assert "goal-allocation" in _RULE_CHECKERS
    assert _RULE_CHECKERS["goal-allocation"] is check_goal_allocation
