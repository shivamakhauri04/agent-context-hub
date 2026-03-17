"""Short selling / Reg SHO checker."""
from __future__ import annotations


def check_short_selling(portfolio: dict) -> list[str]:
    """Check short selling compliance with Reg SHO.

    Skips if no ``short_positions``.  Flags:
    - CRITICAL if any short position lacks a locate
    - CRITICAL if short margin equity / short market value < 0.30
    - WARNING if threshold security held short > 13 days
    - WARNING if hard-to-borrow with annualized rate > 50%
    """
    violations: list[str] = []
    short_positions = portfolio.get("short_positions", [])

    if not short_positions:
        return violations

    # Locate requirement (Reg SHO Rule 203(b))
    for pos in short_positions:
        symbol = pos.get("symbol", "???")
        if not pos.get("locate_obtained", False):
            violations.append(
                f"SHORT CRITICAL: {symbol} short position without locate "
                f"-- Reg SHO Rule 203(b) violation."
            )

    # Margin maintenance check
    short_equity = portfolio.get("short_margin_equity", 0)
    short_mv = portfolio.get("short_market_value", 0)
    if short_mv > 0:
        margin_ratio = short_equity / short_mv
        if margin_ratio < 0.30:
            violations.append(
                f"SHORT CRITICAL: Short margin ratio {margin_ratio:.1%} below "
                f"130% maintenance requirement -- forced buy-in risk."
            )

    # Threshold securities and HTB checks
    threshold_list = set(portfolio.get("threshold_securities", []))
    for pos in short_positions:
        symbol = pos.get("symbol", "???")
        days_short = pos.get("days_short", 0)

        if (symbol in threshold_list or pos.get("is_threshold_security")) and days_short > 13:
            violations.append(
                f"SHORT WARNING: {symbol} is a threshold security held short "
                f"for {days_short} days -- close-out deadline approaching."
            )

        if pos.get("is_hard_to_borrow") and pos.get("borrow_rate_annualized", 0) > 50:
            rate = pos["borrow_rate_annualized"]
            violations.append(
                f"SHORT WARNING: {symbol} hard-to-borrow at {rate:.0f}% "
                f"annualized borrow rate -- significant carrying cost."
            )

    return violations
