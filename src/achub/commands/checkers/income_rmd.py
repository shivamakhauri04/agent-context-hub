"""Income portfolio and RMD checker."""
from __future__ import annotations

# IRS Uniform Lifetime Table (partial, ages 73-85)
_UNIFORM_LIFETIME_DIVISORS = {
    73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9,
    78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5,
    83: 17.7, 84: 16.8, 85: 16.0,
}


def check_income_rmd(portfolio: dict) -> list[str]:
    """Check income portfolio and RMD compliance.

    Skips if no ``rmd_config``.  Flags:
    - CRITICAL if RMD required but not scheduled
    - WARNING if scheduled RMD amount is below calculated minimum
    - WARNING if withdrawal rate exceeds 4% in non-RMD context
    - WARNING if equity allocation exceeds 60% for age 73+
    """
    violations: list[str] = []
    config = portfolio.get("rmd_config")

    if not config:
        return violations

    _check_rmd_not_scheduled(portfolio, config, violations)
    _check_rmd_amount_too_low(portfolio, config, violations)
    _check_high_withdrawal_rate(config, violations)
    _check_high_equity_for_age(portfolio, config, violations)

    return violations


def _check_rmd_not_scheduled(
    portfolio: dict, config: dict, violations: list[str]
) -> None:
    age = portfolio.get("account_holder_age", 0)
    rmd_required = config.get("rmd_required", False)
    scheduled = config.get("rmd_amount_scheduled", 0)
    if rmd_required and age >= 73 and scheduled <= 0:
        violations.append(
            f"RMD CRITICAL: Account holder age {age}, RMD is required "
            f"but no distribution is scheduled. Missing the December 31 "
            f"deadline triggers a 25% excise tax penalty."
        )


def _check_rmd_amount_too_low(
    portfolio: dict, config: dict, violations: list[str]
) -> None:
    age = portfolio.get("account_holder_age", 0)
    rmd_required = config.get("rmd_required", False)
    scheduled = config.get("rmd_amount_scheduled", 0)
    prior_balance = config.get("prior_year_end_balance", 0)

    if not rmd_required or age < 73 or scheduled <= 0 or prior_balance <= 0:
        return

    divisor = _UNIFORM_LIFETIME_DIVISORS.get(age)
    if not divisor:
        return

    minimum_rmd = prior_balance / divisor
    if scheduled < minimum_rmd:
        violations.append(
            f"RMD WARNING: Scheduled RMD ${scheduled:,.0f} is below "
            f"calculated minimum ${minimum_rmd:,.0f} "
            f"(${prior_balance:,.0f} / {divisor}). Shortfall of "
            f"${minimum_rmd - scheduled:,.0f} subject to 25% penalty."
        )


def _check_high_withdrawal_rate(
    config: dict, violations: list[str]
) -> None:
    rate = config.get("withdrawal_rate_pct", 0)
    rmd_required = config.get("rmd_required", False)
    if rate > 4.0 and not rmd_required:
        violations.append(
            f"INCOME WARNING: Withdrawal rate {rate:.1f}% exceeds "
            f"the 4% guideline. Increased risk of portfolio depletion "
            f"over a 30-year retirement horizon."
        )


def _check_high_equity_for_age(
    portfolio: dict, config: dict, violations: list[str]
) -> None:
    age = portfolio.get("account_holder_age", 0)
    equity_pct = config.get("income_equity_pct", 0)
    if age >= 73 and equity_pct > 60:
        violations.append(
            f"INCOME WARNING: Equity allocation {equity_pct:.0f}% is "
            f"above 60% for age {age}. High sequence-of-returns risk "
            f"during withdrawal phase."
        )
