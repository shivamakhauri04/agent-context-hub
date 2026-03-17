"""IRA / retirement account compliance checker."""
from __future__ import annotations

# 2025-2026 IRS contribution limits
_LIMIT_UNDER_50 = 7000
_LIMIT_50_PLUS = 8000

# Roth MAGI phase-out thresholds (2025-2026)
_ROTH_PHASEOUT: dict[str, tuple[int, int]] = {
    "single": (150_000, 165_000),
    "married_filing_jointly": (236_000, 246_000),
    "married_filing_separately": (0, 10_000),
}


def check_ira_compliance(portfolio: dict) -> list[str]:
    """Check IRA contribution limits, Roth eligibility, and early withdrawal.

    Skips if ``ira_type`` is not set (not an IRA account). Returns a list of
    violation strings with severity prefixes.
    """
    violations: list[str] = []

    ira_type = portfolio.get("ira_type")
    if not ira_type:
        return violations

    age = portfolio.get("account_holder_age", 0)
    limit = _LIMIT_50_PLUS if age >= 50 else _LIMIT_UNDER_50
    ytd = portfolio.get("ira_contribution_ytd", 0)

    # --- Contribution limit checks ---
    if ytd > limit:
        violations.append(
            f"IRA CRITICAL: Contribution ${ytd:,.0f} exceeds "
            f"{'catch-up ' if age >= 50 else ''}limit ${limit:,} "
            f"— 6% IRS excise tax on excess."
        )
    elif ytd > limit * 0.9:
        violations.append(
            f"IRA WARNING: Contribution ${ytd:,.0f} is above 90% "
            f"of ${limit:,} annual limit — {limit - ytd:,.0f} remaining."
        )

    # --- Roth income eligibility ---
    if ira_type == "roth":
        magi = portfolio.get("magi", 0)
        filing = portfolio.get("filing_status", "single")
        lower, upper = _ROTH_PHASEOUT.get(filing, (150_000, 165_000))

        if magi > upper:
            violations.append(
                f"IRA CRITICAL: MAGI ${magi:,.0f} exceeds Roth "
                f"upper limit ${upper:,} for {filing} "
                f"— contributions not allowed."
            )
        elif magi > lower:
            violations.append(
                f"IRA WARNING: MAGI ${magi:,.0f} is in Roth phase-out "
                f"range (${lower:,}-${upper:,}) for {filing} "
                f"— reduced contribution allowed."
            )

    # --- Early withdrawal penalty ---
    withdrawal = portfolio.get("withdrawal_amount", 0)
    if withdrawal > 0 and age < 59.5:
        violations.append(
            f"IRA WARNING: Withdrawal ${withdrawal:,.0f} before age "
            f"59.5 (current age: {age}) incurs 10% early withdrawal penalty."
        )

    return violations
