"""Cash management / sweep program checker."""
from __future__ import annotations

_FDIC_LIMIT = 250_000


def check_cash_management(portfolio: dict) -> list[str]:
    """Check cash management compliance: FDIC limits, idle cash, SIPC sublimit.

    Skips when ``cash_management_config`` is absent.  Flags:
    - CRITICAL if any single bank exceeds $250,000 FDIC limit
    - WARNING if idle cash exceeds 5% of equity (non-exempt accounts)
    - WARNING if money market sweep cash exceeds $250,000 SIPC sublimit
    """
    violations: list[str] = []
    config = portfolio.get("cash_management_config")
    if not config:
        return violations

    sweep_banks = config.get("sweep_banks", [])
    external_deposits = config.get("external_deposits_same_banks", [])

    # Build external deposits lookup by bank name
    external_by_bank: dict[str, float] = {}
    for dep in external_deposits:
        name = dep.get("bank_name", "")
        external_by_bank[name] = external_by_bank.get(name, 0) + dep.get("amount", 0)

    # 1. FDIC per-bank limit
    for bank in sweep_banks:
        bank_name = bank.get("bank_name", "???")
        sweep_amount = bank.get("deposit_amount", 0)
        external_amount = external_by_bank.get(bank_name, 0)
        total_at_bank = sweep_amount + external_amount

        if total_at_bank > _FDIC_LIMIT:
            uninsured = total_at_bank - _FDIC_LIMIT
            violations.append(
                f"CASH CRITICAL: {bank_name} total deposits ${total_at_bank:,.0f} "
                f"exceed $250,000 FDIC limit — ${uninsured:,.0f} uninsured."
            )

    # 2. Idle cash too high
    equity = portfolio.get("equity", 0)
    cash = portfolio.get("cash", 0)
    idle_exempt = config.get("idle_cash_exempt", False)

    if not idle_exempt and equity > 0 and cash > 0.05 * equity:
        cash_pct = cash / equity
        violations.append(
            f"CASH WARNING: Idle cash ${cash:,.0f} is {cash_pct:.1%} of equity "
            f"(> 5% threshold). Consider investing or increasing DCA."
        )

    # 3. SIPC cash sublimit for money market sweep
    sweep_type = config.get("sweep_type", "")
    if sweep_type == "money_market":
        total_sweep = sum(b.get("deposit_amount", 0) for b in sweep_banks)
        if total_sweep > _FDIC_LIMIT:
            violations.append(
                f"CASH WARNING: Money market sweep total ${total_sweep:,.0f} "
                f"exceeds $250,000 SIPC cash sublimit — "
                f"excess not protected against broker failure."
            )

    return violations
