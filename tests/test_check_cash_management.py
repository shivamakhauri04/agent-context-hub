"""Tests for cash management / sweep program checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.cash_management import check_cash_management


def test_fdic_limit_exceeded_critical() -> None:
    """Single bank sweep + external > $250K -> CRITICAL."""
    portfolio = {
        "equity": 500000,
        "cash": 10000,
        "cash_management_config": {
            "sweep_type": "bank_deposit",
            "sweep_banks": [
                {"bank_name": "Bank A", "deposit_amount": 200000},
            ],
            "external_deposits_same_banks": [
                {"bank_name": "Bank A", "amount": 100000},
            ],
            "idle_cash_exempt": True,
        },
    }
    violations = check_cash_management(portfolio)
    assert any("CRITICAL" in v and "Bank A" in v and "FDIC" in v for v in violations)


def test_fdic_within_limit_clean() -> None:
    """All banks under $250K -> no FDIC violation."""
    portfolio = {
        "equity": 500000,
        "cash": 10000,
        "cash_management_config": {
            "sweep_type": "bank_deposit",
            "sweep_banks": [
                {"bank_name": "Bank A", "deposit_amount": 200000},
                {"bank_name": "Bank B", "deposit_amount": 200000},
            ],
            "external_deposits_same_banks": [],
            "idle_cash_exempt": True,
        },
    }
    violations = check_cash_management(portfolio)
    assert not any("FDIC" in v for v in violations)


def test_idle_cash_warning() -> None:
    """Cash > 5% of equity (non-exempt) -> WARNING."""
    portfolio = {
        "equity": 100000,
        "cash": 8000,
        "cash_management_config": {
            "sweep_type": "bank_deposit",
            "sweep_banks": [],
            "external_deposits_same_banks": [],
            "idle_cash_exempt": False,
        },
    }
    violations = check_cash_management(portfolio)
    assert any("WARNING" in v and "Idle cash" in v for v in violations)


def test_idle_cash_exempt_skips() -> None:
    """Cash > 5% but exempt -> no idle cash warning."""
    portfolio = {
        "equity": 100000,
        "cash": 20000,
        "cash_management_config": {
            "sweep_type": "bank_deposit",
            "sweep_banks": [],
            "external_deposits_same_banks": [],
            "idle_cash_exempt": True,
        },
    }
    violations = check_cash_management(portfolio)
    assert not any("Idle cash" in v for v in violations)


def test_sipc_sublimit_warning() -> None:
    """Money market sweep > $250K -> WARNING."""
    portfolio = {
        "equity": 500000,
        "cash": 10000,
        "cash_management_config": {
            "sweep_type": "money_market",
            "sweep_banks": [
                {"bank_name": "SPAXX", "deposit_amount": 300000},
            ],
            "external_deposits_same_banks": [],
            "idle_cash_exempt": True,
        },
    }
    violations = check_cash_management(portfolio)
    assert any("WARNING" in v and "SIPC" in v for v in violations)


def test_skip_when_config_absent() -> None:
    """No cash_management_config -> skip."""
    portfolio = {"equity": 100000, "cash": 50000}
    violations = check_cash_management(portfolio)
    assert violations == []


def test_checker_registered() -> None:
    """'cash-management' should be in _RULE_CHECKERS."""
    assert "cash-management" in _RULE_CHECKERS
    assert _RULE_CHECKERS["cash-management"] is check_cash_management
