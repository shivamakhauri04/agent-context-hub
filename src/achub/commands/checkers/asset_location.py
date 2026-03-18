"""Asset location (tax placement) checker."""
from __future__ import annotations

_TAX_ADVANTAGED_TYPES = {"traditional_ira", "roth_ira", "401k", "403b"}


def check_asset_location(portfolio: dict) -> list[str]:
    """Check asset location across household accounts for tax efficiency.

    Skips if no ``household_accounts``.  Flags:
    - WARNING if bonds held in taxable when tax-advantaged space available
    - WARNING if REITs held in taxable when tax-advantaged space available
    - WARNING if municipal bonds held in tax-advantaged accounts
    """
    violations: list[str] = []
    accounts = portfolio.get("household_accounts", [])

    if not accounts:
        return violations

    has_tax_advantaged = any(
        a.get("account_tax_type", "") in _TAX_ADVANTAGED_TYPES
        for a in accounts
    )

    for account in accounts:
        acct_type = account.get("account_tax_type", "")
        acct_id = account.get("account_id", "unknown")
        holdings = account.get("holdings", [])

        if acct_type == "taxable":
            _check_taxable_holdings(
                holdings, acct_id, has_tax_advantaged, violations
            )
        elif acct_type in _TAX_ADVANTAGED_TYPES:
            _check_tax_advantaged_holdings(
                holdings, acct_id, acct_type, violations
            )

    return violations


def _check_taxable_holdings(
    holdings: list[dict],
    account_id: str,
    has_tax_advantaged: bool,
    violations: list[str],
) -> None:
    if not has_tax_advantaged:
        return
    for h in holdings:
        category = h.get("asset_category", "").lower()
        pct = h.get("allocation_pct", 0)

        if "bond" in category and "municipal" not in category and pct > 20:
            violations.append(
                f"LOCATION WARNING: Taxable account '{account_id}' holds "
                f"{pct:.0f}% bonds -- consider moving to tax-advantaged "
                f"account for tax efficiency."
            )
        if "reit" in category and pct > 0:
            violations.append(
                f"LOCATION WARNING: Taxable account '{account_id}' holds "
                f"REITs ({pct:.0f}%) -- REIT distributions are ordinary "
                f"income, move to IRA/401k."
            )


def _check_tax_advantaged_holdings(
    holdings: list[dict],
    account_id: str,
    account_tax_type: str,
    violations: list[str],
) -> None:
    for h in holdings:
        category = h.get("asset_category", "").lower()
        pct = h.get("allocation_pct", 0)
        if "municipal" in category and pct > 0:
            violations.append(
                f"LOCATION WARNING: {account_tax_type} account "
                f"'{account_id}' holds municipal bonds ({pct:.0f}%) -- "
                f"municipal bonds are already tax-exempt, wasting "
                f"tax-advantaged space."
            )
