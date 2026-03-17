"""Tests for 0DTE options checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.zero_dte import check_zero_dte


def test_zero_dte_exercise_exceeds_equity_critical() -> None:
    """Short 0DTE with exercise cost > equity -> CRITICAL."""
    portfolio = {
        "equity": 50000,
        "zero_dte_positions": [
            {
                "symbol": "SPX_P5200",
                "direction": "short",
                "max_loss": 3000,
                "exercise_cost": 520000,
                "contracts": 1,
            },
        ],
        "options_approval_level": 4,
    }
    violations = check_zero_dte(portfolio)
    assert any("CRITICAL" in v and "exercise cost" in v.lower() for v in violations)


def test_zero_dte_position_size_exceeds_max_warning() -> None:
    """Total max loss > portfolio allocation limit -> WARNING."""
    portfolio = {
        "equity": 50000,
        "zero_dte_positions": [
            {
                "symbol": "SPX_C5250",
                "direction": "long",
                "max_loss": 4000,
                "exercise_cost": 0,
                "contracts": 5,
            },
        ],
        "zero_dte_max_portfolio_pct": 0.05,
        "options_approval_level": 3,
    }
    violations = check_zero_dte(portfolio)
    # 4000 > 50000 * 0.05 = 2500
    assert any("WARNING" in v and "portfolio limit" in v.lower() for v in violations)


def test_zero_dte_low_approval_short_warning() -> None:
    """Short 0DTE with approval level < 3 -> WARNING."""
    portfolio = {
        "equity": 100000,
        "zero_dte_positions": [
            {
                "symbol": "AAPL_P190",
                "direction": "short",
                "max_loss": 500,
                "exercise_cost": 19000,
                "contracts": 1,
            },
        ],
        "options_approval_level": 2,
    }
    violations = check_zero_dte(portfolio)
    assert any("WARNING" in v and "approval" in v.lower() for v in violations)


def test_zero_dte_within_limits_pass() -> None:
    """All positions within limits -> no CRITICAL/WARNING."""
    portfolio = {
        "equity": 100000,
        "zero_dte_positions": [
            {
                "symbol": "SPX_C5250",
                "direction": "long",
                "max_loss": 1000,
                "exercise_cost": 0,
                "contracts": 1,
            },
        ],
        "zero_dte_max_portfolio_pct": 0.05,
        "options_approval_level": 3,
    }
    violations = check_zero_dte(portfolio)
    critical_warning = [v for v in violations if "CRITICAL" in v or "WARNING" in v]
    assert critical_warning == []


def test_zero_dte_no_positions_skips() -> None:
    """No 0DTE positions -> skip entirely."""
    portfolio = {"equity": 100000, "zero_dte_positions": []}
    violations = check_zero_dte(portfolio)
    assert violations == []


def test_zero_dte_checker_registered() -> None:
    """'zero-dte' should be in _RULE_CHECKERS."""
    assert "zero-dte" in _RULE_CHECKERS
    assert _RULE_CHECKERS["zero-dte"] is check_zero_dte
