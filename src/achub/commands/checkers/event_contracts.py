"""Event contracts / prediction markets checker."""
from __future__ import annotations

_FINANCE_CATEGORIES = frozenset({
    "finance", "financial", "stock_market", "interest_rates", "economics",
})


def check_event_contracts(portfolio: dict) -> list[str]:
    """Check event contract compliance: position limits, collateral, concentration.

    Skips when ``event_contract_config`` is absent.  Flags:
    - CRITICAL if total exposure exceeds platform position limit
    - CRITICAL if collateral is insufficient to cover positions
    - WARNING if any single event exceeds 25% of equity
    - WARNING if finance-category events exceed 10% of equity
    """
    violations: list[str] = []
    config = portfolio.get("event_contract_config")
    if not config:
        return violations

    equity = portfolio.get("equity", 0)
    total_exposure = config.get("total_exposure_usd", 0)
    limit = config.get("platform_position_limit_usd", 0)
    collateral = config.get("collateral_available", 0)
    positions = config.get("positions", [])

    # 1. Position limit exceeded
    if limit > 0 and total_exposure > limit:
        violations.append(
            f"EVENT CONTRACT CRITICAL: Total exposure ${total_exposure:,.0f} "
            f"exceeds platform position limit ${limit:,.0f}."
        )

    # 2. Collateral shortfall
    required_collateral = sum(
        p.get("contracts", 0) * p.get("price_per_contract", 0) for p in positions
    )
    if required_collateral > collateral:
        violations.append(
            f"EVENT CONTRACT CRITICAL: Required collateral ${required_collateral:,.0f} "
            f"exceeds available collateral ${collateral:,.0f}."
        )

    if equity <= 0:
        return violations

    # 3. Single event concentration
    for pos in positions:
        pos_value = pos.get("contracts", 0) * pos.get("price_per_contract", 0)
        if pos_value > 0.25 * equity:
            event_id = pos.get("event_id", "???")
            pct = pos_value / equity
            violations.append(
                f"EVENT CONTRACT WARNING: Event '{event_id}' exposure "
                f"${pos_value:,.0f} is {pct:.0%} of equity "
                f"(> 25% concentration threshold)."
            )

    # 4. Finance-category correlation
    finance_exposure = sum(
        p.get("contracts", 0) * p.get("price_per_contract", 0)
        for p in positions
        if p.get("event_category", "").lower() in _FINANCE_CATEGORIES
    )
    if finance_exposure > 0.10 * equity:
        pct = finance_exposure / equity
        violations.append(
            f"EVENT CONTRACT WARNING: Finance-category exposure "
            f"${finance_exposure:,.0f} is {pct:.0%} of equity "
            f"(> 10% — correlated speculation risk)."
        )

    return violations
