"""Crypto compliance checker for digital asset positions."""
from __future__ import annotations


def check_crypto(portfolio: dict) -> list[str]:
    """Check crypto compliance rules.

    Skips if ``crypto_config`` is absent.  Flags:
    - CRITICAL if crypto positions lack SIPC awareness disclosure
    - CRITICAL if crypto sold at loss and repurchased within 30 days (2025+ wash sale)
    - WARNING if crypto allocation exceeds cap
    - WARNING if staking rewards > $600 YTD without tax flag
    - WARNING if wash sale tracking is disabled
    """
    violations: list[str] = []

    config = portfolio.get("crypto_config")
    if not config:
        return violations

    if not config.get("sipc_awareness_disclosed", False):
        positions = config.get("crypto_positions", [])
        if positions:
            violations.append(
                "CRYPTO CRITICAL: Crypto positions held without SIPC awareness "
                "disclosure -- crypto is NOT covered by SIPC insurance."
            )

    for sale in config.get("recent_crypto_sales_at_loss", []):
        if sale.get("repurchased_within_30d", False):
            symbol = sale.get("symbol", "UNKNOWN")
            loss = sale.get("loss_usd", 0)
            violations.append(
                f"CRYPTO CRITICAL: {symbol} sold at ${loss:,.2f} loss and "
                f"repurchased within 30 days -- crypto wash sale rule "
                f"(effective 2025) disallows this loss deduction."
            )

    allocation_pct = config.get("crypto_allocation_pct", 0)
    cap_pct = config.get("crypto_allocation_cap_pct", 100)
    if allocation_pct > cap_pct:
        violations.append(
            f"CRYPTO WARNING: Crypto allocation {allocation_pct:.1f}% exceeds "
            f"cap of {cap_pct:.1f}% -- portfolio is over-concentrated in crypto."
        )

    for pos in config.get("crypto_positions", []):
        if pos.get("is_staking", False):
            rewards = pos.get("staking_rewards_ytd_usd", 0)
            if rewards > 600:
                symbol = pos.get("symbol", "UNKNOWN")
                violations.append(
                    f"CRYPTO WARNING: {symbol} staking rewards ${rewards:,.2f} "
                    f"exceed $600 YTD -- requires 1099-MISC tax reporting."
                )

    if not config.get("wash_sale_tracking_enabled", True):
        violations.append(
            "CRYPTO WARNING: Wash sale tracking is disabled for crypto "
            "account -- required for 2025+ digital asset wash sale compliance."
        )

    return violations
