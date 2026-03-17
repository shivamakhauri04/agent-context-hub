"""Recurring investments / DCA checker."""
from __future__ import annotations

from datetime import datetime


def check_recurring(portfolio: dict) -> list[str]:
    """Check recurring investment configuration for issues.

    Skips if no ``recurring_investments``.  Flags:
    - WARNING if monthly recurring total exceeds available cash
    - WARNING if any recurring symbol overlaps with recent loss sale (wash sale)
    - CAUTION if monthly recurring total exceeds 10% of equity
    """
    violations: list[str] = []
    recurring = portfolio.get("recurring_investments", [])

    if not recurring:
        return violations

    cash = portfolio.get("cash", 0)
    equity = portfolio.get("equity", 0)
    monthly_total = portfolio.get("recurring_total_monthly_usd", 0)

    if monthly_total <= 0:
        monthly_total = _estimate_monthly_total(recurring)

    if monthly_total > cash:
        violations.append(
            f"RECURRING WARNING: Monthly recurring investments ${monthly_total:,.0f} "
            f"exceed available cash ${cash:,.0f} -- insufficient funds risk."
        )

    # Check wash sale conflict with recent loss sales
    recent_trades = portfolio.get("recent_trades", [])
    recurring_symbols = {inv.get("symbol", "").upper() for inv in recurring}
    loss_symbols = _recent_loss_symbols(recent_trades)

    overlap = recurring_symbols & loss_symbols
    if overlap:
        symbols_str = ", ".join(sorted(overlap))
        violations.append(
            f"RECURRING WARNING: Recurring investment in {symbols_str} "
            f"conflicts with recent loss sale -- wash sale risk."
        )

    if equity > 0 and monthly_total > equity * 0.10:
        violations.append(
            f"RECURRING CAUTION: Monthly recurring ${monthly_total:,.0f} exceeds "
            f"10% of equity (${equity * 0.10:,.0f})."
        )

    return violations


def _estimate_monthly_total(recurring: list[dict]) -> float:
    """Estimate monthly total from individual recurring configs."""
    _freq_multiplier = {
        "daily": 21,
        "weekly": 4.33,
        "biweekly": 2.17,
        "monthly": 1,
    }
    total = 0.0
    for inv in recurring:
        amount = inv.get("amount_usd", 0)
        freq = inv.get("frequency", "monthly")
        total += amount * _freq_multiplier.get(freq, 1)
    return total


def _recent_loss_symbols(trades: list[dict]) -> set[str]:
    """Extract symbols with loss sales in the last 30 days."""
    loss_symbols: set[str] = set()
    now = datetime.now()

    for trade in trades:
        action = trade.get("action", trade.get("side", "")).lower()
        if action != "sell":
            continue
        pnl = trade.get("pnl", trade.get("realized_pnl", 0))
        if pnl >= 0:
            continue

        date_str = trade.get("date", "")
        if not date_str:
            continue
        try:
            trade_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        if abs((now - trade_date).days) <= 30:
            loss_symbols.add(trade.get("symbol", "").upper())

    return loss_symbols
