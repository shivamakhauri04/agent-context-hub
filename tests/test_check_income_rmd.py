"""Tests for income portfolio and RMD checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.income_rmd import check_income_rmd


def test_rmd_not_scheduled_critical() -> None:
    """RMD required, age 75, no distribution scheduled -> CRITICAL."""
    portfolio = {
        "account_holder_age": 75,
        "rmd_config": {
            "rmd_required": True,
            "prior_year_end_balance": 500000,
            "rmd_amount_scheduled": 0,
            "rmd_amount_taken_ytd": 0,
            "withdrawal_rate_pct": 0,
            "income_equity_pct": 40,
        },
    }
    violations = check_income_rmd(portfolio)
    assert any("CRITICAL" in v and "no distribution" in v.lower() for v in violations)


def test_rmd_scheduled_passes() -> None:
    """RMD required and properly scheduled -> no CRITICAL for scheduling."""
    portfolio = {
        "account_holder_age": 75,
        "rmd_config": {
            "rmd_required": True,
            "prior_year_end_balance": 500000,
            "rmd_amount_scheduled": 25000,
            "rmd_amount_taken_ytd": 0,
            "withdrawal_rate_pct": 3.5,
            "income_equity_pct": 40,
        },
    }
    violations = check_income_rmd(portfolio)
    scheduling = [v for v in violations if "no distribution" in v.lower()]
    assert scheduling == []


def test_rmd_amount_too_low_warning() -> None:
    """Scheduled RMD below calculated minimum -> WARNING."""
    portfolio = {
        "account_holder_age": 75,
        "rmd_config": {
            "rmd_required": True,
            "prior_year_end_balance": 500000,
            "rmd_amount_scheduled": 15000,
            "rmd_amount_taken_ytd": 0,
            "withdrawal_rate_pct": 3.0,
            "income_equity_pct": 40,
        },
    }
    violations = check_income_rmd(portfolio)
    # Minimum RMD = 500000 / 24.6 = $20,325
    assert any("WARNING" in v and "below" in v.lower() for v in violations)


def test_rmd_amount_sufficient_passes() -> None:
    """Scheduled RMD meets minimum -> no WARNING about amount."""
    portfolio = {
        "account_holder_age": 75,
        "rmd_config": {
            "rmd_required": True,
            "prior_year_end_balance": 500000,
            "rmd_amount_scheduled": 25000,
            "rmd_amount_taken_ytd": 0,
            "withdrawal_rate_pct": 3.5,
            "income_equity_pct": 40,
        },
    }
    violations = check_income_rmd(portfolio)
    amount_warnings = [v for v in violations if "below" in v.lower() and "WARNING" in v]
    assert amount_warnings == []


def test_high_withdrawal_rate_warning() -> None:
    """Withdrawal rate >4% without RMD requirement -> WARNING."""
    portfolio = {
        "account_holder_age": 65,
        "rmd_config": {
            "rmd_required": False,
            "prior_year_end_balance": 800000,
            "rmd_amount_scheduled": 0,
            "rmd_amount_taken_ytd": 0,
            "withdrawal_rate_pct": 6.0,
            "income_equity_pct": 50,
        },
    }
    violations = check_income_rmd(portfolio)
    assert any("WARNING" in v and "withdrawal rate" in v.lower() for v in violations)


def test_high_equity_for_age_warning() -> None:
    """Age 76 with 75% equity allocation -> WARNING."""
    portfolio = {
        "account_holder_age": 76,
        "rmd_config": {
            "rmd_required": True,
            "prior_year_end_balance": 400000,
            "rmd_amount_scheduled": 20000,
            "rmd_amount_taken_ytd": 0,
            "withdrawal_rate_pct": 3.5,
            "income_equity_pct": 75,
        },
    }
    violations = check_income_rmd(portfolio)
    assert any("WARNING" in v and "equity" in v.lower() for v in violations)


def test_income_rmd_no_config_skips() -> None:
    """No rmd_config -> empty list."""
    portfolio = {"equity": 500000}
    violations = check_income_rmd(portfolio)
    assert violations == []


def test_income_rmd_checker_registered() -> None:
    """'income-rmd' should be in _RULE_CHECKERS."""
    assert "income-rmd" in _RULE_CHECKERS
    assert _RULE_CHECKERS["income-rmd"] is check_income_rmd
