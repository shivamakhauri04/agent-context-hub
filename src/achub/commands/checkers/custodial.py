"""Custodial account (UTMA/UGMA) checker."""
from __future__ import annotations

_KIDDIE_TAX_THRESHOLD = 2600


def check_custodial(portfolio: dict) -> list[str]:
    """Check custodial account compliance: prohibited instruments, kiddie tax, majority.

    Skips when ``custodial_config`` is absent or ``is_custodial`` is false.  Flags:
    - CRITICAL if options, margin, futures, or short positions in custodial account
    - WARNING if unearned income exceeds $2,600 kiddie tax threshold
    - INFO if minor is within 1 year of age of majority
    """
    violations: list[str] = []
    config = portfolio.get("custodial_config")
    if not config or not config.get("is_custodial", False):
        return violations

    # 1. Prohibited instruments
    prohibited = []
    if config.get("has_options"):
        prohibited.append("options")
    if config.get("has_margin"):
        prohibited.append("margin")
    if config.get("has_futures"):
        prohibited.append("futures")
    if config.get("has_short_positions"):
        prohibited.append("short positions")

    if prohibited:
        instruments = ", ".join(prohibited)
        violations.append(
            f"CUSTODIAL CRITICAL: Prohibited instruments in custodial account: "
            f"{instruments}. UTMA/UGMA accounts cannot hold these."
        )

    # 2. Kiddie tax threshold
    unearned_income = config.get("unearned_income_ytd", 0)
    if unearned_income > _KIDDIE_TAX_THRESHOLD:
        excess = unearned_income - _KIDDIE_TAX_THRESHOLD
        violations.append(
            f"CUSTODIAL WARNING: Unearned income ${unearned_income:,.0f} exceeds "
            f"${_KIDDIE_TAX_THRESHOLD:,} kiddie tax threshold — "
            f"${excess:,.0f} taxed at parent's marginal rate."
        )

    # 3. Approaching age of majority
    minor_age = config.get("minor_age", 0)
    majority_age = config.get("state_age_of_majority", 18)
    if minor_age >= majority_age - 1 and minor_age < majority_age:
        violations.append(
            f"CUSTODIAL INFO: Minor is {minor_age}, approaching age of majority "
            f"({majority_age}). Prepare for irrevocable transfer of assets."
        )

    return violations
