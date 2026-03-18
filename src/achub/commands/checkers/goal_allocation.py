"""Goal-based allocation checker."""
from __future__ import annotations


def check_goal_allocation(portfolio: dict) -> list[str]:
    """Check goal allocation configuration for issues.

    Skips if no ``goal_type`` set.  Flags:
    - WARNING if equity too high for short time horizon
    - CRITICAL if emergency fund has equity allocation
    - WARNING if risk score and equity allocation mismatch
    - WARNING if goal configured but no customer risk score
    """
    violations: list[str] = []
    goal_type = portfolio.get("goal_type")

    if not goal_type:
        return violations

    equity_pct = portfolio.get("goal_equity_pct", 0)
    horizon = portfolio.get("goal_time_horizon_years", 0)
    risk_score = portfolio.get("customer_risk_score")

    if horizon < 3 and equity_pct > 30:
        violations.append(
            f"GOAL WARNING: Equity allocation {equity_pct:.0f}% too high "
            f"for {horizon}-year goal horizon (max 30% recommended)."
        )

    if goal_type == "emergency_fund" and equity_pct > 0:
        violations.append(
            f"GOAL CRITICAL: Emergency fund has {equity_pct:.0f}% equity "
            f"allocation -- must be 100% cash/money market."
        )

    if risk_score is not None and risk_score <= 3 and equity_pct > 60:
        violations.append(
            f"GOAL WARNING: Conservative risk score ({risk_score}) but "
            f"{equity_pct:.0f}% equity allocation -- exceeds 60% maximum "
            f"for conservative profiles."
        )

    if risk_score is None:
        violations.append(
            f"GOAL WARNING: Goal type '{goal_type}' configured but no "
            f"customer_risk_score set -- allocation may be unsuitable."
        )

    return violations
