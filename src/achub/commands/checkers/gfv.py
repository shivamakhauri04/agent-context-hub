"""Good Faith Violation (GFV) checker for cash accounts."""
from __future__ import annotations


def check_gfv(portfolio: dict) -> list[str]:
    """Check Good Faith Violation risk for cash accounts.

    Skips if ``account_type`` is not ``"cash"``.  Flags:
    - CRITICAL if 3+ GFV in 12 months (account restricted)
    - WARNING if 2 GFV (one more triggers restriction)
    - WARNING if pending buy uses unsettled funds
    - CAUTION if unsettled cash exists with active sell positions
    """
    violations: list[str] = []

    if portfolio.get("account_type", "").lower() != "cash":
        return violations

    gfv_count = portfolio.get("gfv_count_12m", 0)

    if gfv_count >= 3:
        violations.append(
            f"GFV CRITICAL: {gfv_count} Good Faith Violations in 12 months "
            f"-- cash account restricted to settled-cash trading for 90 days."
        )
    elif gfv_count == 2:
        violations.append(
            "GFV WARNING: 2 Good Faith Violations in 12 months "
            "-- next violation triggers 90-day settled-cash restriction."
        )

    if portfolio.get("pending_buy_with_unsettled"):
        violations.append(
            "GFV WARNING: Pending buy order uses unsettled funds "
            "-- will trigger a Good Faith Violation if executed."
        )

    unsettled = portfolio.get("unsettled_cash", 0)
    if unsettled > 0 and gfv_count < 3:
        positions = portfolio.get("positions", [])
        if positions:
            violations.append(
                f"GFV CAUTION: ${unsettled:,.2f} unsettled cash with active "
                f"positions -- selling before settlement could trigger GFV."
            )

    return violations
