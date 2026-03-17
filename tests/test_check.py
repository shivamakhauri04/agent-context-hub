from __future__ import annotations

from achub.commands.check import _check_pdt, _check_wash_sale


def test_pdt_violation_detected() -> None:
    """Margin account, <$25k equity, 3 day trades -> warns about 4th."""
    portfolio = {
        "account_type": "margin",
        "equity": 20000,
        "day_trades_count_5d": 3,
    }
    warnings = _check_pdt(portfolio)
    assert len(warnings) == 1
    assert "PDT" in warnings[0]
    assert "3 day trades" in warnings[0]


def test_pdt_no_violation_cash() -> None:
    """Cash account with 3 day trades -> no PDT warning."""
    portfolio = {
        "account_type": "cash",
        "equity": 10000,
        "day_trades_count_5d": 3,
    }
    warnings = _check_pdt(portfolio)
    assert warnings == []


def test_pdt_no_violation_above_25k() -> None:
    """Margin account, $30k equity, 3 day trades -> no warning."""
    portfolio = {
        "account_type": "margin",
        "equity": 30000,
        "day_trades_count_5d": 3,
    }
    warnings = _check_pdt(portfolio)
    assert warnings == []


def test_wash_sale_detected() -> None:
    """TSLA sold at loss 15 days ago and repurchased -> violation."""
    portfolio = {
        "recent_trades": [
            {
                "symbol": "TSLA",
                "side": "sell",
                "quantity": 10,
                "price": 165.00,
                "date": "2026-03-01",
                "realized_pnl": -2500.00,
            },
            {
                "symbol": "TSLA",
                "side": "buy",
                "quantity": 10,
                "price": 170.00,
                "date": "2026-03-16",
                "realized_pnl": 0,
            },
        ],
        "positions": [],
    }
    warnings = _check_wash_sale(portfolio)
    assert len(warnings) >= 1
    assert any("WASH SALE" in w and "TSLA" in w for w in warnings)


def test_wash_sale_detected_action_pnl_fields() -> None:
    """TSLA sold at loss using action/pnl fields (sample_portfolio.json format)."""
    portfolio = {
        "recent_trades": [
            {
                "symbol": "TSLA",
                "action": "sell",
                "quantity": 10,
                "price": 165.00,
                "date": "2026-03-01",
                "pnl": -2500.00,
            },
            {
                "symbol": "TSLA",
                "action": "buy",
                "quantity": 10,
                "price": 170.00,
                "date": "2026-03-16",
                "pnl": 0,
            },
        ],
        "positions": [],
    }
    warnings = _check_wash_sale(portfolio)
    assert len(warnings) >= 1
    assert any("WASH SALE" in w and "TSLA" in w for w in warnings)


def test_wash_sale_no_violation() -> None:
    """TSLA sold at loss 45 days ago and repurchased -> no violation."""
    portfolio = {
        "recent_trades": [
            {
                "symbol": "TSLA",
                "side": "sell",
                "quantity": 10,
                "price": 165.00,
                "date": "2026-01-30",
                "realized_pnl": -2500.00,
            },
            {
                "symbol": "TSLA",
                "side": "buy",
                "quantity": 10,
                "price": 170.00,
                "date": "2026-03-16",
                "realized_pnl": 0,
            },
        ],
        "positions": [],
    }
    warnings = _check_wash_sale(portfolio)
    assert warnings == []
