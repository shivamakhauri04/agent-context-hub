from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.futures import check_futures_margin


def _make_portfolio(
    positions: list[dict],
    balance: float,
    day_trade: bool = False,
) -> dict:
    return {
        "asset_class": "futures",
        "futures_positions": positions,
        "futures_account_balance": balance,
        "futures_day_trade": day_trade,
    }


def test_futures_below_maintenance_single() -> None:
    """/ES x2, balance $20k (maint $23k) -> CRITICAL."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/ES", "contracts": 2}],
        balance=20000,
    )
    violations = check_futures_margin(portfolio)
    assert any("CRITICAL" in v and "/ES" in v for v in violations)


def test_futures_above_maintenance_single() -> None:
    """/ES x1, balance $15k (maint $11.5k) -> pass."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/ES", "contracts": 1}],
        balance=15000,
    )
    violations = check_futures_margin(portfolio)
    critical = [v for v in violations if "CRITICAL" in v]
    assert critical == []


def test_futures_below_initial_margin() -> None:
    """/MES x5, balance $5k (initial $6,325) -> WARNING."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/MES", "contracts": 5}],
        balance=5000,
    )
    violations = check_futures_margin(portfolio)
    # Maintenance for 5 /MES = 5 * $1,150 = $5,750 > $5,000 -> CRITICAL
    # Initial for 5 /MES = 5 * $1,265 = $6,325 > $5,000
    assert any("CRITICAL" in v or "WARNING" in v for v in violations)


def test_futures_day_trade_margin() -> None:
    """/ES x1, day_trade=True, balance $5k -> WARNING or CRITICAL."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/ES", "contracts": 1}],
        balance=5000,
        day_trade=True,
    )
    violations = check_futures_margin(portfolio)
    # Day trade maintenance = $11,500 * 0.5 = $5,750 > $5,000 -> CRITICAL
    assert any("CRITICAL" in v for v in violations)


def test_futures_day_trade_sufficient() -> None:
    """/MES x2, day_trade=True, balance $2k -> pass."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/MES", "contracts": 2}],
        balance=2000,
        day_trade=True,
    )
    violations = check_futures_margin(portfolio)
    # Day trade maintenance for 2 /MES = 2 * $1,150 * 0.5 = $1,150 < $2,000
    critical = [v for v in violations if "CRITICAL" in v]
    assert critical == []


def test_futures_unknown_contract() -> None:
    """/ZZ x1 -> WARNING "Unknown contract"."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/ZZ", "contracts": 1}],
        balance=10000,
    )
    violations = check_futures_margin(portfolio)
    assert any("Unknown contract" in v and "/ZZ" in v for v in violations)


def test_futures_multiple_positions() -> None:
    """/ES x1 + /NQ x1, balance $20k -> WARNING (below aggregate initial)."""
    portfolio = _make_portfolio(
        positions=[
            {"symbol": "/ES", "contracts": 1},
            {"symbol": "/NQ", "contracts": 1},
        ],
        balance=20000,
    )
    violations = check_futures_margin(portfolio)
    # Each passes maintenance individually, but total initial $30,250 > $20,000
    assert any("WARNING" in v for v in violations)


def test_futures_non_futures_skips() -> None:
    """asset_class='equity' -> pass (skip futures checks)."""
    portfolio = {
        "asset_class": "equity",
        "futures_positions": [{"symbol": "/ES", "contracts": 2}],
        "futures_account_balance": 100,
    }
    violations = check_futures_margin(portfolio)
    assert violations == []


def test_futures_empty_positions() -> None:
    """futures_positions=[] -> pass."""
    portfolio = _make_portfolio(positions=[], balance=10000)
    violations = check_futures_margin(portfolio)
    assert violations == []


def test_futures_zero_contracts() -> None:
    """/ES x0 -> pass."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/ES", "contracts": 0}],
        balance=10000,
    )
    violations = check_futures_margin(portfolio)
    assert violations == []


def test_futures_short_position() -> None:
    """/ES x-2 -> uses abs(), CRITICAL if underfunded."""
    portfolio = _make_portfolio(
        positions=[{"symbol": "/ES", "contracts": -2}],
        balance=20000,
    )
    violations = check_futures_margin(portfolio)
    # abs(-2) = 2, maintenance = 2 * $11,500 = $23,000 > $20,000
    assert any("CRITICAL" in v and "/ES" in v for v in violations)


def test_futures_checker_registered() -> None:
    """'futures' should be in _RULE_CHECKERS."""
    assert "futures" in _RULE_CHECKERS
    assert _RULE_CHECKERS["futures"] is check_futures_margin
