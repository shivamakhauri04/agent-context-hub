"""Tests for Good Faith Violation checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.gfv import check_gfv


def test_gfv_3_violations_critical() -> None:
    """3+ GFV in 12 months -> CRITICAL."""
    portfolio = {
        "account_type": "cash",
        "gfv_count_12m": 3,
        "unsettled_cash": 0,
        "pending_buy_with_unsettled": False,
    }
    violations = check_gfv(portfolio)
    assert any("CRITICAL" in v and "90 days" in v for v in violations)


def test_gfv_2_violations_warning() -> None:
    """2 GFV in 12 months -> WARNING."""
    portfolio = {
        "account_type": "cash",
        "gfv_count_12m": 2,
        "unsettled_cash": 0,
        "pending_buy_with_unsettled": False,
    }
    violations = check_gfv(portfolio)
    assert any("WARNING" in v and "next violation" in v for v in violations)


def test_gfv_pending_unsettled_buy() -> None:
    """Pending buy with unsettled funds -> WARNING."""
    portfolio = {
        "account_type": "cash",
        "gfv_count_12m": 0,
        "unsettled_cash": 5000,
        "pending_buy_with_unsettled": True,
    }
    violations = check_gfv(portfolio)
    assert any("WARNING" in v and "unsettled funds" in v for v in violations)


def test_gfv_cash_account_only() -> None:
    """Cash account with issues -> violations found."""
    portfolio = {
        "account_type": "cash",
        "gfv_count_12m": 3,
    }
    violations = check_gfv(portfolio)
    assert len(violations) >= 1


def test_gfv_non_cash_skips() -> None:
    """Margin account -> skip GFV checks entirely."""
    portfolio = {
        "account_type": "margin",
        "gfv_count_12m": 5,
        "pending_buy_with_unsettled": True,
    }
    violations = check_gfv(portfolio)
    assert violations == []


def test_gfv_zero_clean() -> None:
    """Zero GFV, no unsettled, no pending -> pass."""
    portfolio = {
        "account_type": "cash",
        "gfv_count_12m": 0,
        "unsettled_cash": 0,
        "pending_buy_with_unsettled": False,
    }
    violations = check_gfv(portfolio)
    assert violations == []


def test_gfv_checker_registered() -> None:
    """'gfv' should be in _RULE_CHECKERS."""
    assert "gfv" in _RULE_CHECKERS
    assert _RULE_CHECKERS["gfv"] is check_gfv
