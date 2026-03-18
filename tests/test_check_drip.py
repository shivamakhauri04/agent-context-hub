"""Tests for DRIP (dividend reinvestment plan) checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.drip import check_drip


def test_drip_tlh_conflict_critical() -> None:
    """DRIP on VOO while harvest_opportunities has VOO -> CRITICAL."""
    portfolio = {
        "drip_enabled_symbols": ["VOO"],
        "harvest_opportunities": [
            {
                "symbol": "VOO",
                "unrealized_loss": 3000,
                "holding_days": 200,
                "proposed_replacement": "VTI",
            },
        ],
        "recurring_investments": [],
    }
    violations = check_drip(portfolio)
    assert any("CRITICAL" in v and "voo" in v.lower() for v in violations)


def test_drip_dca_overlap_warning() -> None:
    """DRIP on AAPL while recurring_investments has AAPL -> WARNING."""
    portfolio = {
        "drip_enabled_symbols": ["AAPL"],
        "harvest_opportunities": [],
        "recurring_investments": [
            {"symbol": "AAPL", "amount_usd": 200, "frequency": "monthly"},
        ],
    }
    violations = check_drip(portfolio)
    assert any("WARNING" in v and "aapl" in v.lower() for v in violations)


def test_drip_no_conflicts_passes() -> None:
    """DRIP on AAPL with no overlap -> no violations."""
    portfolio = {
        "drip_enabled_symbols": ["AAPL"],
        "harvest_opportunities": [],
        "recurring_investments": [
            {"symbol": "VOO", "amount_usd": 500, "frequency": "monthly"},
        ],
    }
    violations = check_drip(portfolio)
    assert violations == []


def test_drip_no_drip_symbols_skips() -> None:
    """Empty drip_enabled_symbols -> empty list."""
    portfolio = {
        "drip_enabled_symbols": [],
        "harvest_opportunities": [],
        "recurring_investments": [],
    }
    violations = check_drip(portfolio)
    assert violations == []


def test_drip_checker_registered() -> None:
    """'drip' should be in _RULE_CHECKERS."""
    assert "drip" in _RULE_CHECKERS
    assert _RULE_CHECKERS["drip"] is check_drip
