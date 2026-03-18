"""Tests for direct indexing checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.direct_indexing import check_direct_indexing


def test_direct_indexing_below_minimum_critical() -> None:
    """Equity below minimum account size -> CRITICAL."""
    portfolio = {
        "equity": 50000,
        "direct_index_config": {
            "benchmark_index": "SP500",
            "minimum_account_size": 100000,
            "individual_positions": [],
            "tracking_error_pct": 0.5,
            "etf_holdings": [],
        },
    }
    violations = check_direct_indexing(portfolio)
    assert any("CRITICAL" in v and "50,000" in v for v in violations)


def test_direct_indexing_above_minimum_passes() -> None:
    """Equity above minimum -> no CRITICAL for minimum."""
    portfolio = {
        "equity": 150000,
        "direct_index_config": {
            "benchmark_index": "SP500",
            "minimum_account_size": 100000,
            "individual_positions": [],
            "tracking_error_pct": 0.5,
            "etf_holdings": [],
        },
    }
    violations = check_direct_indexing(portfolio)
    min_violations = [v for v in violations if "below minimum" in v.lower()]
    assert min_violations == []


def test_direct_indexing_etf_wash_sale_critical() -> None:
    """Stock with loss + ETF tracking same benchmark -> CRITICAL."""
    portfolio = {
        "equity": 200000,
        "direct_index_config": {
            "benchmark_index": "SP500",
            "minimum_account_size": 100000,
            "individual_positions": [
                {"symbol": "AAPL", "weight_pct": 5.0, "unrealized_pnl": -500},
            ],
            "tracking_error_pct": 1.0,
            "etf_holdings": ["VOO"],
        },
    }
    violations = check_direct_indexing(portfolio)
    assert any("CRITICAL" in v and "wash sale" in v.lower() for v in violations)


def test_direct_indexing_etf_no_loss_passes() -> None:
    """Stock with gain + ETF tracking same benchmark -> no wash sale."""
    portfolio = {
        "equity": 200000,
        "direct_index_config": {
            "benchmark_index": "SP500",
            "minimum_account_size": 100000,
            "individual_positions": [
                {"symbol": "AAPL", "weight_pct": 5.0, "unrealized_pnl": 500},
            ],
            "tracking_error_pct": 1.0,
            "etf_holdings": ["VOO"],
        },
    }
    violations = check_direct_indexing(portfolio)
    wash = [v for v in violations if "wash sale" in v.lower()]
    assert wash == []


def test_direct_indexing_tracking_error_warning() -> None:
    """Tracking error above 2% -> WARNING."""
    portfolio = {
        "equity": 200000,
        "direct_index_config": {
            "benchmark_index": "SP500",
            "minimum_account_size": 100000,
            "individual_positions": [],
            "tracking_error_pct": 3.5,
            "etf_holdings": [],
        },
    }
    violations = check_direct_indexing(portfolio)
    assert any("WARNING" in v and "tracking error" in v.lower() for v in violations)


def test_direct_indexing_tracking_error_ok() -> None:
    """Tracking error below 2% -> no WARNING."""
    portfolio = {
        "equity": 200000,
        "direct_index_config": {
            "benchmark_index": "SP500",
            "minimum_account_size": 100000,
            "individual_positions": [],
            "tracking_error_pct": 1.5,
            "etf_holdings": [],
        },
    }
    violations = check_direct_indexing(portfolio)
    te_warnings = [v for v in violations if "tracking error" in v.lower()]
    assert te_warnings == []


def test_direct_indexing_no_config_skips() -> None:
    """No direct_index_config -> empty list."""
    portfolio = {"equity": 100000}
    violations = check_direct_indexing(portfolio)
    assert violations == []


def test_direct_indexing_checker_registered() -> None:
    """'direct-indexing' should be in _RULE_CHECKERS."""
    assert "direct-indexing" in _RULE_CHECKERS
    assert _RULE_CHECKERS["direct-indexing"] is check_direct_indexing
