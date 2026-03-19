"""Alternative investments compliance checker."""
from __future__ import annotations

_HIGH_EXPENSE_RATIO_PCT = 1.0
_MIN_EXPERIENCE_LEVEL = 3


def check_alt_investments(portfolio: dict) -> list[str]:
    """Check alternative investments compliance: accreditation, concentration, expenses.

    Skips when ``alt_investment_config`` is absent.  Flags:
    - CRITICAL if non-accredited investor holds non-ETF alternatives
    - WARNING if total alt allocation exceeds cap percentage
    - WARNING if any alt position has expense ratio > 1.0%
    - WARNING if customer experience level < 3 with alt positions
    """
    violations: list[str] = []
    config = portfolio.get("alt_investment_config")
    if not config:
        return violations

    positions = config.get("alt_positions", [])
    if not positions:
        return violations

    is_accredited = config.get("is_accredited_investor", False)
    equity = portfolio.get("equity", 0)
    cap_pct = config.get("alt_allocation_cap_pct", 20)
    experience = portfolio.get("customer_experience_level", 1)

    # 1. Not accredited for non-ETF alts
    if not is_accredited:
        non_etf = [p for p in positions if not p.get("is_liquid_alt_etf", False)]
        if non_etf:
            symbols = ", ".join(p.get("symbol", "???") for p in non_etf)
            violations.append(
                f"ALT INVESTMENT CRITICAL: Non-accredited investor holds "
                f"non-ETF alternatives: {symbols}. "
                f"Accredited investor status required."
            )

    # 2. Concentration exceeds cap
    total_alt_value = sum(p.get("value_usd", 0) for p in positions)
    if equity > 0:
        alt_pct = (total_alt_value / equity) * 100
        if alt_pct > cap_pct:
            violations.append(
                f"ALT INVESTMENT WARNING: Alt allocation {alt_pct:.1f}% "
                f"exceeds {cap_pct:.0f}% cap "
                f"(${total_alt_value:,.0f} of ${equity:,.0f} equity)."
            )

    # 3. High expense ratio
    for pos in positions:
        expense = pos.get("expense_ratio_pct", 0)
        if expense > _HIGH_EXPENSE_RATIO_PCT:
            symbol = pos.get("symbol", "???")
            violations.append(
                f"ALT INVESTMENT WARNING: {symbol} expense ratio {expense:.2f}% "
                f"exceeds {_HIGH_EXPENSE_RATIO_PCT:.1f}% threshold."
            )

    # 4. Low experience level
    if experience < _MIN_EXPERIENCE_LEVEL:
        violations.append(
            f"ALT INVESTMENT WARNING: Customer experience level {experience} "
            f"is below minimum {_MIN_EXPERIENCE_LEVEL} for alternative investments."
        )

    return violations
