"""Tests for tax-loss harvesting checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.tlh import check_tlh


def test_tlh_substantially_identical_critical() -> None:
    """Harvest VOO with replacement IVV (same SP500 index) -> CRITICAL."""
    portfolio = {
        "harvest_opportunities": [
            {
                "symbol": "VOO",
                "unrealized_loss": 3000,
                "holding_days": 200,
                "proposed_replacement": "IVV",
            },
        ],
        "capital_gains_ytd": 0,
        "capital_losses_ytd": 0,
        "ira_recent_purchases": [],
    }
    violations = check_tlh(portfolio)
    assert any("CRITICAL" in v and "voo" in v.lower() for v in violations)


def test_tlh_safe_replacement_passes() -> None:
    """Harvest VOO with replacement VTI (different index) -> no CRITICAL."""
    portfolio = {
        "harvest_opportunities": [
            {
                "symbol": "VOO",
                "unrealized_loss": 3000,
                "holding_days": 200,
                "proposed_replacement": "VTI",
            },
        ],
        "capital_gains_ytd": 0,
        "capital_losses_ytd": 0,
        "ira_recent_purchases": [],
    }
    violations = check_tlh(portfolio)
    critical = [v for v in violations if "CRITICAL" in v]
    assert critical == []


def test_tlh_annual_cap_exceeded_warning() -> None:
    """Net capital losses exceed $3,000 annual deduction cap -> WARNING."""
    portfolio = {
        "harvest_opportunities": [
            {
                "symbol": "MSFT",
                "unrealized_loss": 500,
                "holding_days": 100,
                "proposed_replacement": "GOOG",
            },
        ],
        "capital_gains_ytd": 2000,
        "capital_losses_ytd": 8000,
        "ira_recent_purchases": [],
    }
    violations = check_tlh(portfolio)
    assert any("WARNING" in v and "cap" in v.lower() for v in violations)


def test_tlh_annual_cap_within_limit() -> None:
    """Net capital losses within $3,000 cap -> no WARNING about cap."""
    portfolio = {
        "harvest_opportunities": [
            {
                "symbol": "MSFT",
                "unrealized_loss": 500,
                "holding_days": 100,
                "proposed_replacement": "GOOG",
            },
        ],
        "capital_gains_ytd": 1000,
        "capital_losses_ytd": 2000,
        "ira_recent_purchases": [],
    }
    violations = check_tlh(portfolio)
    cap_warnings = [v for v in violations if "WARNING" in v and "cap" in v.lower()]
    assert cap_warnings == []


def test_tlh_ira_cross_account_critical() -> None:
    """Harvest AAPL while IRA recently bought AAPL -> CRITICAL."""
    portfolio = {
        "harvest_opportunities": [
            {
                "symbol": "AAPL",
                "unrealized_loss": 1000,
                "holding_days": 90,
                "proposed_replacement": "MSFT",
            },
        ],
        "capital_gains_ytd": 0,
        "capital_losses_ytd": 0,
        "ira_recent_purchases": [
            {"symbol": "AAPL", "date": "2026-03-10"},
        ],
    }
    violations = check_tlh(portfolio)
    assert any("CRITICAL" in v and "ira" in v.lower() for v in violations)


def test_tlh_short_term_priority_info() -> None:
    """Long-term loss available when short-term loss also available -> INFO."""
    portfolio = {
        "harvest_opportunities": [
            {
                "symbol": "VOO",
                "unrealized_loss": 2000,
                "holding_days": 400,
                "proposed_replacement": "VTI",
            },
            {
                "symbol": "AAPL",
                "unrealized_loss": 3000,
                "holding_days": 100,
                "proposed_replacement": "MSFT",
            },
        ],
        "capital_gains_ytd": 0,
        "capital_losses_ytd": 0,
        "ira_recent_purchases": [],
    }
    violations = check_tlh(portfolio)
    assert any("INFO" in v and "short-term" in v.lower() for v in violations)


def test_tlh_no_opportunities_skips() -> None:
    """No harvest opportunities -> empty list."""
    portfolio = {
        "harvest_opportunities": [],
        "capital_gains_ytd": 0,
        "capital_losses_ytd": 0,
        "ira_recent_purchases": [],
    }
    violations = check_tlh(portfolio)
    assert violations == []


def test_tlh_checker_registered() -> None:
    """'tlh' should be in _RULE_CHECKERS."""
    assert "tlh" in _RULE_CHECKERS
    assert _RULE_CHECKERS["tlh"] is check_tlh
