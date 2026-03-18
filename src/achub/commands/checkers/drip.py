"""DRIP (dividend reinvestment plan) checker."""
from __future__ import annotations


def check_drip(portfolio: dict) -> list[str]:
    """Check DRIP configuration for conflicts.

    Skips if no ``drip_enabled_symbols``.  Flags:
    - CRITICAL if DRIP enabled for TLH candidates (wash sale on dividends)
    - WARNING if DRIP and recurring investments overlap (double-buying)
    """
    violations: list[str] = []
    drip_symbols = portfolio.get("drip_enabled_symbols", [])

    if not drip_symbols:
        return violations

    drip_set = {s.upper() for s in drip_symbols}

    # DRIP + TLH conflict
    harvest = portfolio.get("harvest_opportunities", [])
    harvest_symbols = {h.get("symbol", "").upper() for h in harvest}
    tlh_overlap = drip_set & harvest_symbols
    if tlh_overlap:
        symbols_str = ", ".join(sorted(tlh_overlap))
        violations.append(
            f"DRIP CRITICAL: DRIP enabled for {symbols_str} which are "
            f"also TLH candidates -- DRIP will trigger wash sale on "
            f"every dividend. Disable DRIP before harvesting."
        )

    # DRIP + DCA overlap
    recurring = portfolio.get("recurring_investments", [])
    recurring_symbols = {r.get("symbol", "").upper() for r in recurring}
    dca_overlap = drip_set & recurring_symbols
    if dca_overlap:
        symbols_str = ", ".join(sorted(dca_overlap))
        violations.append(
            f"DRIP WARNING: DRIP enabled for {symbols_str} which also "
            f"have recurring investments -- double-buying risk on "
            f"dividend dates."
        )

    return violations
