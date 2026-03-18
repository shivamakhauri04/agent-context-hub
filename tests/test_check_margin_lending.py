"""Tests for margin lending checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.margin_lending import check_margin_lending


def test_margin_lending_ltv_exceeded_critical() -> None:
    """LTV above maintenance threshold -> CRITICAL."""
    portfolio = {
        "margin_loan": {
            "loan_balance": 400000,
            "collateral_value": 500000,
            "maintenance_ltv_pct": 70,
            "interest_rate_annual": 6.5,
            "loan_purpose": "general",
            "largest_collateral_position_pct": 30,
        },
    }
    violations = check_margin_lending(portfolio)
    assert any("CRITICAL" in v and "ltv" in v.lower() for v in violations)


def test_margin_lending_ltv_safe_passes() -> None:
    """LTV well below maintenance threshold -> no violations."""
    portfolio = {
        "margin_loan": {
            "loan_balance": 200000,
            "collateral_value": 500000,
            "maintenance_ltv_pct": 70,
            "interest_rate_annual": 6.5,
            "loan_purpose": "general",
            "largest_collateral_position_pct": 30,
        },
    }
    violations = check_margin_lending(portfolio)
    ltv_violations = [v for v in violations if "ltv" in v.lower()]
    assert ltv_violations == []


def test_margin_lending_ltv_near_threshold_warning() -> None:
    """LTV within 5% of maintenance threshold -> WARNING."""
    portfolio = {
        "margin_loan": {
            "loan_balance": 340000,
            "collateral_value": 500000,
            "maintenance_ltv_pct": 70,
            "interest_rate_annual": 6.5,
            "loan_purpose": "general",
            "largest_collateral_position_pct": 30,
        },
    }
    violations = check_margin_lending(portfolio)
    assert any("WARNING" in v and "within 5%" in v for v in violations)


def test_margin_lending_concentration_warning() -> None:
    """Largest position >50% of collateral -> WARNING."""
    portfolio = {
        "margin_loan": {
            "loan_balance": 200000,
            "collateral_value": 500000,
            "maintenance_ltv_pct": 70,
            "interest_rate_annual": 6.5,
            "loan_purpose": "general",
            "largest_collateral_position_pct": 65,
        },
    }
    violations = check_margin_lending(portfolio)
    assert any("WARNING" in v and "concentration" in v.lower() for v in violations)


def test_margin_lending_reg_u_warning() -> None:
    """Loan purpose is securities purchase -> WARNING."""
    portfolio = {
        "margin_loan": {
            "loan_balance": 100000,
            "collateral_value": 500000,
            "maintenance_ltv_pct": 70,
            "interest_rate_annual": 6.5,
            "loan_purpose": "securities_purchase",
            "largest_collateral_position_pct": 20,
        },
    }
    violations = check_margin_lending(portfolio)
    assert any("WARNING" in v and "regulation u" in v.lower() for v in violations)


def test_margin_lending_no_config_skips() -> None:
    """No margin_loan -> empty list."""
    portfolio = {"equity": 500000}
    violations = check_margin_lending(portfolio)
    assert violations == []


def test_margin_lending_checker_registered() -> None:
    """'margin-lending' should be in _RULE_CHECKERS."""
    assert "margin-lending" in _RULE_CHECKERS
    assert _RULE_CHECKERS["margin-lending"] is check_margin_lending
