"""Futures margin checker."""
from __future__ import annotations

# Per-contract margin requirements (initial, maintenance) in USD.
# Source: CME Group margin schedules (approximate, updated 2026-03).
_FUTURES_MARGINS: dict[str, tuple[float, float]] = {
    "/ES": (12_650, 11_500),
    "/MES": (1_265, 1_150),
    "/NQ": (17_600, 16_000),
    "/MNQ": (1_760, 1_600),
    "/YM": (9_500, 8_600),
    "/MYM": (950, 860),
    "/RTY": (7_150, 6_500),
    "/M2K": (715, 650),
    "/CL": (6_800, 6_200),
    "/MCL": (680, 620),
    "/GC": (10_500, 9_500),
    "/MGC": (1_050, 950),
}

_DAY_TRADE_MARGIN_FACTOR = 0.5


def check_futures_margin(portfolio: dict) -> list[str]:
    """Check futures margin requirements per contract.

    Skips if ``asset_class`` is not ``"futures"`` or ``futures_positions``
    is empty/absent.  Returns a list of violation strings.
    """
    violations: list[str] = []

    if portfolio.get("asset_class", "").lower() != "futures":
        return violations

    positions = portfolio.get("futures_positions", [])
    if not positions:
        return violations

    balance = portfolio.get("futures_account_balance", 0)
    is_day_trade = portfolio.get("futures_day_trade", False)
    total_initial_required = 0.0

    for pos in positions:
        symbol = pos.get("symbol", "").upper()
        contracts = pos.get("contracts", 0)
        if contracts == 0:
            continue

        margins = _FUTURES_MARGINS.get(symbol)
        if margins is None:
            violations.append(
                f"FUTURES WARNING: Unknown contract '{symbol}' "
                f"— cannot verify margin requirements."
            )
            continue

        initial, maintenance = margins
        abs_contracts = abs(contracts)

        if is_day_trade:
            initial = initial * _DAY_TRADE_MARGIN_FACTOR
            maintenance = maintenance * _DAY_TRADE_MARGIN_FACTOR

        maint_required = maintenance * abs_contracts
        if balance < maint_required:
            violations.append(
                f"FUTURES CRITICAL: {symbol} x{contracts} requires "
                f"${maint_required:,.0f} maintenance margin, "
                f"balance is ${balance:,.0f} — "
                f"liquidation within hours."
            )

        total_initial_required += initial * abs_contracts

    if total_initial_required > 0 and balance < total_initial_required:
        has_critical = any("CRITICAL" in v for v in violations)
        if not has_critical:
            violations.append(
                f"FUTURES WARNING: Total initial margin required "
                f"${total_initial_required:,.0f} exceeds balance "
                f"${balance:,.0f} — cannot open new positions."
            )

    return violations
