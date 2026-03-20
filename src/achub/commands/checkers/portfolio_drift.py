"""Portfolio drift monitoring checker."""
from __future__ import annotations

from datetime import datetime


def check_portfolio_drift(portfolio: dict) -> list[str]:
    """Check portfolio drift against target allocations.

    Skips if ``target_allocations`` is absent.  Flags:
    - CRITICAL if any asset class drift > 2x rebalance threshold
    - WARNING if any asset class drift > rebalance threshold
    - WARNING if target allocation percentages don't sum to ~100%
    - WARNING if last rebalance was > 90 days ago
    """
    violations: list[str] = []

    allocations = portfolio.get("target_allocations")
    if not allocations:
        return violations

    threshold = portfolio.get("rebalance_threshold_pct", 5.0)

    target_sum = sum(a.get("target_pct", 0) for a in allocations)
    if abs(target_sum - 100) > 1:
        violations.append(
            f"DRIFT WARNING: Target allocations sum to {target_sum:.1f}% "
            f"(expected ~100%) -- allocation model may be misconfigured."
        )

    for alloc in allocations:
        target = alloc.get("target_pct", 0)
        current = alloc.get("current_pct")
        if current is None:
            continue
        drift = abs(current - target)
        asset_class = alloc.get("asset_class", "unknown")

        if drift > threshold * 2:
            violations.append(
                f"DRIFT CRITICAL: {asset_class} drifted {drift:.1f}% "
                f"(current {current:.1f}% vs target {target:.1f}%) -- "
                f"exceeds 2x rebalance threshold of {threshold:.1f}%."
            )
        elif drift > threshold:
            violations.append(
                f"DRIFT WARNING: {asset_class} drifted {drift:.1f}% "
                f"(current {current:.1f}% vs target {target:.1f}%) -- "
                f"exceeds rebalance threshold of {threshold:.1f}%."
            )

    last_rebalance = portfolio.get("last_rebalance_date")
    if last_rebalance:
        try:
            last_date = datetime.strptime(last_rebalance, "%Y-%m-%d")
            days_since = (datetime.now() - last_date).days
            if days_since > 90:
                violations.append(
                    f"DRIFT WARNING: Last rebalance was {days_since} days ago "
                    f"-- consider rebalancing (recommended at least quarterly)."
                )
        except ValueError:
            pass

    return violations
