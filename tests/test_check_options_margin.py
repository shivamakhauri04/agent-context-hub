"""Tests for options approval and margin maintenance checkers."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.margin import check_margin_maintenance
from achub.commands.checkers.options import check_options_approval

# --- Options approval tests ---


def test_options_above_approval_level() -> None:
    """Level 2 account with pending naked_call (level 5) -> violation."""
    portfolio = {
        "options_approval_level": 2,
        "cash": 50000,
        "pending_options_strategies": [
            {"strategy": "naked_call", "symbol": "TSLA"},
        ],
        "expiring_options": [],
    }
    violations = check_options_approval(portfolio)
    assert len(violations) == 1
    assert "Level 5" in violations[0]
    assert "TSLA" in violations[0]


def test_options_within_approval_level() -> None:
    """Level 3 account with pending debit_spread -> pass."""
    portfolio = {
        "options_approval_level": 3,
        "cash": 50000,
        "pending_options_strategies": [
            {"strategy": "debit_spread", "symbol": "AAPL"},
        ],
        "expiring_options": [],
    }
    violations = check_options_approval(portfolio)
    assert violations == []


def test_options_no_strategies() -> None:
    """Empty strategies list -> no violations."""
    portfolio = {
        "options_approval_level": 1,
        "cash": 50000,
        "pending_options_strategies": [],
        "expiring_options": [],
    }
    violations = check_options_approval(portfolio)
    assert violations == []


def test_options_unknown_strategy() -> None:
    """Unknown strategy name -> violation."""
    portfolio = {
        "options_approval_level": 5,
        "cash": 50000,
        "pending_options_strategies": [
            {"strategy": "triple_butterfly_spread", "symbol": "SPY"},
        ],
        "expiring_options": [],
    }
    violations = check_options_approval(portfolio)
    assert len(violations) == 1
    assert "Unknown strategy" in violations[0]


def test_options_expiration_capital_insufficient() -> None:
    """Expiring ITM option with exercise cost > cash -> warning."""
    portfolio = {
        "options_approval_level": 2,
        "cash": 5000,
        "pending_options_strategies": [],
        "expiring_options": [
            {"symbol": "AAPL_C200", "exercise_cost": 20000},
        ],
    }
    violations = check_options_approval(portfolio)
    assert len(violations) == 1
    assert "exercise cost" in violations[0].lower()
    assert "AAPL_C200" in violations[0]


def test_options_expiration_capital_sufficient() -> None:
    """Expiring ITM option with exercise cost < cash -> pass."""
    portfolio = {
        "options_approval_level": 2,
        "cash": 50000,
        "pending_options_strategies": [],
        "expiring_options": [
            {"symbol": "AAPL_C200", "exercise_cost": 20000},
        ],
    }
    violations = check_options_approval(portfolio)
    assert violations == []


def test_options_multiple_violations() -> None:
    """Multiple bad strategies -> multiple violations."""
    portfolio = {
        "options_approval_level": 1,
        "cash": 50000,
        "pending_options_strategies": [
            {"strategy": "long_call", "symbol": "AAPL"},
            {"strategy": "naked_put", "symbol": "TSLA"},
            {"strategy": "credit_spread", "symbol": "SPY"},
        ],
        "expiring_options": [],
    }
    violations = check_options_approval(portfolio)
    assert len(violations) == 3


# --- Margin maintenance tests ---


def test_margin_below_finra_minimum() -> None:
    """Margin ratio < 25% -> CRITICAL."""
    portfolio = {
        "account_type": "margin",
        "equity": 20000,
        "market_value": 100000,
        "positions": [],
    }
    violations = check_margin_maintenance(portfolio)
    assert len(violations) == 1
    assert "CRITICAL" in violations[0]


def test_margin_below_house_requirement() -> None:
    """Margin ratio between 25% and house (30%) -> WARNING."""
    portfolio = {
        "account_type": "margin",
        "equity": 27000,
        "market_value": 100000,
        "house_margin_requirement": 0.30,
        "positions": [],
    }
    violations = check_margin_maintenance(portfolio)
    assert len(violations) == 1
    assert "WARNING" in violations[0]


def test_margin_approaching_house() -> None:
    """Margin ratio within 5% buffer above house -> CAUTION."""
    portfolio = {
        "account_type": "margin",
        "equity": 32000,
        "market_value": 100000,
        "house_margin_requirement": 0.30,
        "positions": [],
    }
    violations = check_margin_maintenance(portfolio)
    assert len(violations) == 1
    assert "CAUTION" in violations[0]


def test_margin_healthy() -> None:
    """Margin ratio well above house + buffer -> no violations."""
    portfolio = {
        "account_type": "margin",
        "equity": 50000,
        "market_value": 100000,
        "house_margin_requirement": 0.30,
        "positions": [],
    }
    violations = check_margin_maintenance(portfolio)
    assert violations == []


def test_margin_cash_account_exempt() -> None:
    """Cash account -> no violations regardless of ratio."""
    portfolio = {
        "account_type": "cash",
        "equity": 5000,
        "market_value": 100000,
        "positions": [],
    }
    violations = check_margin_maintenance(portfolio)
    assert violations == []


def test_margin_concentrated_position() -> None:
    """>50% single stock -> WARNING."""
    portfolio = {
        "account_type": "margin",
        "equity": 50000,
        "market_value": 100000,
        "house_margin_requirement": 0.30,
        "positions": [
            {"symbol": "NVDA", "quantity": 100, "current_price": 600.00},
        ],
    }
    violations = check_margin_maintenance(portfolio)
    assert any("concentrated" in v.lower() for v in violations)
    assert any("NVDA" in v for v in violations)


def test_margin_zero_market_value() -> None:
    """market_value=0 -> no crash, no violations."""
    portfolio = {
        "account_type": "margin",
        "equity": 0,
        "market_value": 0,
        "positions": [],
    }
    violations = check_margin_maintenance(portfolio)
    assert violations == []


# --- Registration test ---


def test_checkers_registered() -> None:
    """Verify 'options' and 'margin' are in _RULE_CHECKERS."""
    assert "options" in _RULE_CHECKERS
    assert "margin" in _RULE_CHECKERS
    assert _RULE_CHECKERS["options"] is check_options_approval
    assert _RULE_CHECKERS["margin"] is check_margin_maintenance
