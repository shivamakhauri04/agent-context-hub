"""Tests for recurring investments / DCA checker."""
from __future__ import annotations

from datetime import datetime, timedelta

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.recurring import check_recurring


def test_recurring_exceeds_cash_warning() -> None:
    """Monthly recurring total > available cash -> WARNING."""
    portfolio = {
        "cash": 500,
        "equity": 50000,
        "recurring_investments": [
            {"symbol": "VOO", "amount_usd": 1000, "frequency": "monthly"},
        ],
        "recurring_total_monthly_usd": 1000,
    }
    violations = check_recurring(portfolio)
    assert any("WARNING" in v and "cash" in v.lower() for v in violations)


def test_recurring_wash_sale_conflict_warning() -> None:
    """Recurring symbol overlaps with recent loss sale -> WARNING."""
    recent_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    portfolio = {
        "cash": 10000,
        "equity": 50000,
        "recurring_investments": [
            {"symbol": "AAPL", "amount_usd": 100, "frequency": "weekly"},
        ],
        "recurring_total_monthly_usd": 433,
        "recent_trades": [
            {
                "symbol": "AAPL",
                "action": "sell",
                "quantity": 50,
                "price": 170.00,
                "date": recent_date,
                "pnl": -500.00,
            },
        ],
    }
    violations = check_recurring(portfolio)
    assert any("WARNING" in v and "wash sale" in v.lower() for v in violations)


def test_recurring_within_limits_pass() -> None:
    """Recurring within cash and no conflicts -> no WARNING."""
    portfolio = {
        "cash": 10000,
        "equity": 50000,
        "recurring_investments": [
            {"symbol": "VOO", "amount_usd": 200, "frequency": "monthly"},
        ],
        "recurring_total_monthly_usd": 200,
        "recent_trades": [],
    }
    violations = check_recurring(portfolio)
    warning = [v for v in violations if "WARNING" in v]
    assert warning == []


def test_recurring_no_investments_skips() -> None:
    """No recurring investments -> skip entirely."""
    portfolio = {"cash": 10000, "equity": 50000, "recurring_investments": []}
    violations = check_recurring(portfolio)
    assert violations == []


def test_recurring_checker_registered() -> None:
    """'recurring' should be in _RULE_CHECKERS."""
    assert "recurring" in _RULE_CHECKERS
    assert _RULE_CHECKERS["recurring"] is check_recurring
