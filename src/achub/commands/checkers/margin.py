"""Margin maintenance checker."""
from __future__ import annotations


def check_margin_maintenance(portfolio: dict) -> list[str]:
    """Check margin maintenance ratio and concentrated positions.

    Skips if ``account_type`` is not ``"margin"``.  Calculates
    ``margin_ratio = equity / market_value`` and flags:
    - CRITICAL if ratio < 0.25 (FINRA minimum)
    - WARNING if ratio < house_margin_requirement (default 0.30)
    - CAUTION if ratio < house_margin_requirement + 0.05

    Also flags concentrated positions where a single holding exceeds 50% of
    total market value.
    """
    violations: list[str] = []

    if portfolio.get("account_type", "").lower() != "margin":
        return violations

    equity = portfolio.get("equity", 0)
    market_value = portfolio.get("market_value", 0)
    house_req = portfolio.get("house_margin_requirement", 0.30)

    if market_value <= 0:
        return violations

    margin_ratio = equity / market_value

    if margin_ratio < 0.25:
        violations.append(
            f"MARGIN CRITICAL: Margin ratio {margin_ratio:.1%} is below "
            f"FINRA 25% minimum. Margin call imminent."
        )
    elif margin_ratio < house_req:
        violations.append(
            f"MARGIN WARNING: Margin ratio {margin_ratio:.1%} is below "
            f"house requirement {house_req:.0%}."
        )
    elif margin_ratio < house_req + 0.05:
        violations.append(
            f"MARGIN CAUTION: Margin ratio {margin_ratio:.1%} is approaching "
            f"house requirement {house_req:.0%}."
        )

    # Check concentrated positions
    positions = portfolio.get("positions", [])
    for pos in positions:
        qty = pos.get("quantity", 0)
        price = pos.get("current_price", 0)
        pos_value = qty * price
        if pos_value > 0.50 * market_value:
            symbol = pos.get("symbol", "???")
            concentration = pos_value / market_value
            violations.append(
                f"MARGIN WARNING: {symbol} is {concentration:.0%} of portfolio "
                f"— concentrated position may trigger higher margin requirement."
            )

    return violations
