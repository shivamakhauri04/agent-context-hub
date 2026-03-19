"""Tests for event contracts / prediction markets checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.event_contracts import check_event_contracts


def test_position_limit_exceeded_critical() -> None:
    """Total exposure > platform limit -> CRITICAL."""
    portfolio = {
        "equity": 100000,
        "event_contract_config": {
            "positions": [],
            "platform_position_limit_usd": 50000,
            "total_exposure_usd": 55000,
            "collateral_available": 60000,
        },
    }
    violations = check_event_contracts(portfolio)
    assert any("CRITICAL" in v and "position limit" in v for v in violations)


def test_collateral_shortfall_critical() -> None:
    """Required collateral > available -> CRITICAL."""
    portfolio = {
        "equity": 100000,
        "event_contract_config": {
            "positions": [
                {"event_id": "fed-rate", "direction": "yes",
                 "contracts": 1000, "price_per_contract": 0.60,
                 "event_category": "economics"},
            ],
            "platform_position_limit_usd": 50000,
            "total_exposure_usd": 600,
            "collateral_available": 500,
        },
    }
    violations = check_event_contracts(portfolio)
    assert any("CRITICAL" in v and "collateral" in v for v in violations)


def test_single_event_concentration_warning() -> None:
    """Single event > 25% of equity -> WARNING."""
    portfolio = {
        "equity": 10000,
        "event_contract_config": {
            "positions": [
                {"event_id": "election-2026", "direction": "yes",
                 "contracts": 5000, "price_per_contract": 0.60,
                 "event_category": "politics"},
            ],
            "platform_position_limit_usd": 50000,
            "total_exposure_usd": 3000,
            "collateral_available": 5000,
        },
    }
    violations = check_event_contracts(portfolio)
    assert any("WARNING" in v and "concentration" in v for v in violations)


def test_finance_category_correlation_warning() -> None:
    """Finance-category events > 10% of equity -> WARNING."""
    portfolio = {
        "equity": 10000,
        "event_contract_config": {
            "positions": [
                {"event_id": "sp500-above-5500", "direction": "yes",
                 "contracts": 2000, "price_per_contract": 0.55,
                 "event_category": "finance"},
            ],
            "platform_position_limit_usd": 50000,
            "total_exposure_usd": 1100,
            "collateral_available": 5000,
        },
    }
    violations = check_event_contracts(portfolio)
    assert any("WARNING" in v and "correlated" in v for v in violations)


def test_all_clean_no_violations() -> None:
    """Small positions, within limits -> pass."""
    portfolio = {
        "equity": 100000,
        "event_contract_config": {
            "positions": [
                {"event_id": "weather-temp", "direction": "no",
                 "contracts": 100, "price_per_contract": 0.40,
                 "event_category": "weather"},
            ],
            "platform_position_limit_usd": 50000,
            "total_exposure_usd": 40,
            "collateral_available": 5000,
        },
    }
    violations = check_event_contracts(portfolio)
    assert violations == []


def test_skip_when_config_absent() -> None:
    """No event_contract_config -> skip."""
    portfolio = {"equity": 100000}
    violations = check_event_contracts(portfolio)
    assert violations == []


def test_zero_equity_skips_concentration() -> None:
    """Zero equity -> skip concentration checks but still check limits."""
    portfolio = {
        "equity": 0,
        "event_contract_config": {
            "positions": [
                {"event_id": "fed-rate", "direction": "yes",
                 "contracts": 100, "price_per_contract": 0.50,
                 "event_category": "finance"},
            ],
            "platform_position_limit_usd": 50000,
            "total_exposure_usd": 60000,
            "collateral_available": 100,
        },
    }
    violations = check_event_contracts(portfolio)
    # Should still catch position limit and collateral, not concentration
    assert any("CRITICAL" in v for v in violations)
    assert not any("concentration" in v for v in violations)


def test_checker_registered() -> None:
    """'event-contracts' should be in _RULE_CHECKERS."""
    assert "event-contracts" in _RULE_CHECKERS
    assert _RULE_CHECKERS["event-contracts"] is check_event_contracts
