"""Tests for alternative investments compliance checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.alt_investments import check_alt_investments


def test_non_accredited_non_etf_critical() -> None:
    """Non-accredited investor with non-ETF alt -> CRITICAL."""
    portfolio = {
        "equity": 100000,
        "customer_experience_level": 4,
        "alt_investment_config": {
            "is_accredited_investor": False,
            "alt_positions": [
                {"symbol": "HEDGE-FUND-A", "value_usd": 10000,
                 "expense_ratio_pct": 1.5, "is_liquid_alt_etf": False},
            ],
            "alt_allocation_cap_pct": 20,
        },
    }
    violations = check_alt_investments(portfolio)
    assert any("CRITICAL" in v and "HEDGE-FUND-A" in v for v in violations)


def test_accredited_non_etf_clean() -> None:
    """Accredited investor with non-ETF alt -> no accreditation violation."""
    portfolio = {
        "equity": 500000,
        "customer_experience_level": 5,
        "alt_investment_config": {
            "is_accredited_investor": True,
            "alt_positions": [
                {"symbol": "PRIV-FUND", "value_usd": 50000,
                 "expense_ratio_pct": 0.8, "is_liquid_alt_etf": False},
            ],
            "alt_allocation_cap_pct": 20,
        },
    }
    violations = check_alt_investments(portfolio)
    assert not any("accredited" in v.lower() for v in violations)


def test_concentration_exceeds_cap_warning() -> None:
    """Total alts > cap percentage -> WARNING."""
    portfolio = {
        "equity": 100000,
        "customer_experience_level": 4,
        "alt_investment_config": {
            "is_accredited_investor": True,
            "alt_positions": [
                {"symbol": "QAI", "value_usd": 15000,
                 "expense_ratio_pct": 0.5, "is_liquid_alt_etf": True},
                {"symbol": "BTAL", "value_usd": 10000,
                 "expense_ratio_pct": 0.6, "is_liquid_alt_etf": True},
            ],
            "alt_allocation_cap_pct": 20,
        },
    }
    violations = check_alt_investments(portfolio)
    assert any("WARNING" in v and "allocation" in v for v in violations)


def test_high_expense_ratio_warning() -> None:
    """Alt with expense ratio > 1.0% -> WARNING."""
    portfolio = {
        "equity": 100000,
        "customer_experience_level": 4,
        "alt_investment_config": {
            "is_accredited_investor": True,
            "alt_positions": [
                {"symbol": "ALTS-X", "value_usd": 5000,
                 "expense_ratio_pct": 1.85, "is_liquid_alt_etf": True},
            ],
            "alt_allocation_cap_pct": 20,
        },
    }
    violations = check_alt_investments(portfolio)
    assert any("WARNING" in v and "expense ratio" in v for v in violations)


def test_low_experience_warning() -> None:
    """Experience level < 3 -> WARNING."""
    portfolio = {
        "equity": 100000,
        "customer_experience_level": 2,
        "alt_investment_config": {
            "is_accredited_investor": True,
            "alt_positions": [
                {"symbol": "QAI", "value_usd": 5000,
                 "expense_ratio_pct": 0.5, "is_liquid_alt_etf": True},
            ],
            "alt_allocation_cap_pct": 20,
        },
    }
    violations = check_alt_investments(portfolio)
    assert any("WARNING" in v and "experience" in v for v in violations)


def test_clean_alt_portfolio() -> None:
    """Within all limits -> pass."""
    portfolio = {
        "equity": 200000,
        "customer_experience_level": 4,
        "alt_investment_config": {
            "is_accredited_investor": True,
            "alt_positions": [
                {"symbol": "QAI", "value_usd": 10000,
                 "expense_ratio_pct": 0.5, "is_liquid_alt_etf": True},
            ],
            "alt_allocation_cap_pct": 20,
        },
    }
    violations = check_alt_investments(portfolio)
    assert violations == []


def test_skip_when_config_absent() -> None:
    """No alt_investment_config -> skip."""
    portfolio = {"equity": 100000}
    violations = check_alt_investments(portfolio)
    assert violations == []


def test_checker_registered() -> None:
    """'alt-investments' should be in _RULE_CHECKERS."""
    assert "alt-investments" in _RULE_CHECKERS
    assert _RULE_CHECKERS["alt-investments"] is check_alt_investments
