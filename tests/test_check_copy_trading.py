"""Tests for copy trading checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.copy_trading import check_copy_trading


def test_copy_trading_risk_mismatch_critical() -> None:
    """Leader risk 8 > customer tolerance 2 -> CRITICAL."""
    portfolio = {
        "equity": 50000,
        "customer_risk_tolerance": 2,
        "copy_trading_config": {
            "leader_username": "aggressive_trader",
            "leader_risk_level": 8,
            "copy_allocation_usd": 5000,
            "leader_portfolio_size": 500000,
            "leader_uses_margin": False,
            "leader_uses_options": False,
        },
    }
    violations = check_copy_trading(portfolio)
    assert any("CRITICAL" in v and "risk" in v.lower() for v in violations)


def test_copy_trading_risk_within_tolerance_passes() -> None:
    """Leader risk 3 <= customer tolerance 4 -> no CRITICAL."""
    portfolio = {
        "equity": 50000,
        "customer_risk_tolerance": 4,
        "copy_trading_config": {
            "leader_username": "moderate_trader",
            "leader_risk_level": 3,
            "copy_allocation_usd": 5000,
            "leader_portfolio_size": 100000,
            "leader_uses_margin": False,
            "leader_uses_options": False,
        },
    }
    violations = check_copy_trading(portfolio)
    risk_violations = [v for v in violations if "CRITICAL" in v]
    assert risk_violations == []


def test_copy_trading_concentration_warning() -> None:
    """Copy allocation >25% of equity -> WARNING."""
    portfolio = {
        "equity": 10000,
        "customer_risk_tolerance": 5,
        "copy_trading_config": {
            "leader_username": "trader",
            "leader_risk_level": 3,
            "copy_allocation_usd": 5000,
            "leader_portfolio_size": 100000,
            "leader_uses_margin": False,
            "leader_uses_options": False,
        },
    }
    violations = check_copy_trading(portfolio)
    assert any("WARNING" in v and "concentration" in v.lower() for v in violations)


def test_copy_trading_size_ratio_warning() -> None:
    """Leader 1M vs copier 1K -> size ratio >100x -> WARNING."""
    portfolio = {
        "equity": 1000,
        "customer_risk_tolerance": 5,
        "copy_trading_config": {
            "leader_username": "whale",
            "leader_risk_level": 3,
            "copy_allocation_usd": 1000,
            "leader_portfolio_size": 1000000,
            "leader_uses_margin": False,
            "leader_uses_options": False,
        },
    }
    violations = check_copy_trading(portfolio)
    assert any("WARNING" in v and "rounding" in v.lower() for v in violations)


def test_copy_trading_ira_margin_warning() -> None:
    """IRA copying leader with margin -> WARNING."""
    portfolio = {
        "equity": 50000,
        "customer_risk_tolerance": 5,
        "ira_type": "roth",
        "copy_trading_config": {
            "leader_username": "margin_trader",
            "leader_risk_level": 4,
            "copy_allocation_usd": 5000,
            "leader_portfolio_size": 100000,
            "leader_uses_margin": True,
            "leader_uses_options": True,
        },
    }
    violations = check_copy_trading(portfolio)
    assert any("WARNING" in v and "ira" in v.lower() for v in violations)


def test_copy_trading_no_config_skips() -> None:
    """No copy_trading_config -> empty list."""
    portfolio = {"equity": 50000}
    violations = check_copy_trading(portfolio)
    assert violations == []


def test_copy_trading_checker_registered() -> None:
    """'copy-trading' should be in _RULE_CHECKERS."""
    assert "copy-trading" in _RULE_CHECKERS
    assert _RULE_CHECKERS["copy-trading"] is check_copy_trading
