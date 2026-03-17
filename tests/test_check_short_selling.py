"""Tests for short selling / Reg SHO checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.short_selling import check_short_selling


def test_short_no_locate_critical() -> None:
    """Short position without locate -> CRITICAL."""
    portfolio = {
        "short_positions": [
            {"symbol": "GME", "quantity": 100, "locate_obtained": False},
        ],
        "short_margin_equity": 50000,
        "short_market_value": 30000,
    }
    violations = check_short_selling(portfolio)
    assert any("CRITICAL" in v and "locate" in v.lower() for v in violations)


def test_short_below_maintenance_critical() -> None:
    """Short margin ratio below 30% -> CRITICAL."""
    portfolio = {
        "short_positions": [
            {"symbol": "TSLA", "quantity": 100, "locate_obtained": True},
        ],
        "short_margin_equity": 20000,
        "short_market_value": 100000,
    }
    violations = check_short_selling(portfolio)
    assert any("CRITICAL" in v and "maintenance" in v.lower() for v in violations)


def test_short_threshold_security_warning() -> None:
    """Threshold security held > 13 days -> WARNING."""
    portfolio = {
        "short_positions": [
            {
                "symbol": "BBBY",
                "quantity": 100,
                "locate_obtained": True,
                "is_threshold_security": True,
                "days_short": 15,
            },
        ],
        "threshold_securities": ["BBBY"],
        "short_margin_equity": 50000,
        "short_market_value": 30000,
    }
    violations = check_short_selling(portfolio)
    assert any("WARNING" in v and "threshold" in v.lower() for v in violations)


def test_short_htb_expensive_warning() -> None:
    """Hard-to-borrow with rate > 50% -> WARNING."""
    portfolio = {
        "short_positions": [
            {
                "symbol": "GME",
                "quantity": 100,
                "locate_obtained": True,
                "is_hard_to_borrow": True,
                "borrow_rate_annualized": 120,
                "days_short": 5,
            },
        ],
        "short_margin_equity": 50000,
        "short_market_value": 30000,
    }
    violations = check_short_selling(portfolio)
    assert any("WARNING" in v and "hard-to-borrow" in v.lower() for v in violations)


def test_short_margin_adequate_pass() -> None:
    """All locates obtained, margin adequate -> pass (no CRITICAL)."""
    portfolio = {
        "short_positions": [
            {
                "symbol": "AAPL",
                "quantity": 50,
                "locate_obtained": True,
                "is_hard_to_borrow": False,
                "borrow_rate_annualized": 2,
                "days_short": 3,
            },
        ],
        "short_margin_equity": 50000,
        "short_market_value": 30000,
    }
    violations = check_short_selling(portfolio)
    critical = [v for v in violations if "CRITICAL" in v]
    assert critical == []


def test_short_no_positions_skips() -> None:
    """No short positions -> skip entirely."""
    portfolio = {"short_positions": [], "short_margin_equity": 50000}
    violations = check_short_selling(portfolio)
    assert violations == []


def test_short_selling_checker_registered() -> None:
    """'short-selling' should be in _RULE_CHECKERS."""
    assert "short-selling" in _RULE_CHECKERS
    assert _RULE_CHECKERS["short-selling"] is check_short_selling
