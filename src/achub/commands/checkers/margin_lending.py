"""Margin lending / securities-based lending checker."""
from __future__ import annotations


def check_margin_lending(portfolio: dict) -> list[str]:
    """Check margin lending (securities-based lending) for issues.

    Skips if no ``margin_loan``.  Flags:
    - CRITICAL if LTV exceeds maintenance threshold
    - WARNING if LTV is within 5% of maintenance threshold
    - WARNING if largest collateral position exceeds 50%
    - WARNING if loan purpose is securities purchase (Reg U)
    """
    violations: list[str] = []
    loan = portfolio.get("margin_loan")

    if not loan:
        return violations

    _check_ltv_exceeded(loan, violations)
    _check_ltv_near_threshold(loan, violations)
    _check_concentration(loan, violations)
    _check_reg_u(loan, violations)

    return violations


def _check_ltv_exceeded(loan: dict, violations: list[str]) -> None:
    balance = loan.get("loan_balance", 0)
    collateral = loan.get("collateral_value", 0)
    maintenance_pct = loan.get("maintenance_ltv_pct", 70)
    if collateral <= 0:
        return
    ltv = balance / collateral * 100
    if ltv > maintenance_pct:
        violations.append(
            f"MARGIN LENDING CRITICAL: LTV {ltv:.1f}% exceeds "
            f"maintenance threshold {maintenance_pct}%. "
            f"Forced liquidation may begin immediately."
        )


def _check_ltv_near_threshold(loan: dict, violations: list[str]) -> None:
    balance = loan.get("loan_balance", 0)
    collateral = loan.get("collateral_value", 0)
    maintenance_pct = loan.get("maintenance_ltv_pct", 70)
    if collateral <= 0:
        return
    ltv = balance / collateral * 100
    if ltv <= maintenance_pct and ltv > maintenance_pct - 5:
        violations.append(
            f"MARGIN LENDING WARNING: LTV {ltv:.1f}% is within 5% of "
            f"maintenance threshold {maintenance_pct}%. "
            f"A small market decline could trigger forced liquidation."
        )


def _check_concentration(loan: dict, violations: list[str]) -> None:
    largest_pct = loan.get("largest_collateral_position_pct", 0)
    if largest_pct > 50:
        violations.append(
            f"MARGIN LENDING WARNING: Largest collateral position is "
            f"{largest_pct:.0f}% of total collateral -- concentration "
            f"reduces effective LTV and increases liquidation risk."
        )


def _check_reg_u(loan: dict, violations: list[str]) -> None:
    purpose = loan.get("loan_purpose", "")
    if purpose == "securities_purchase":
        violations.append(
            "MARGIN LENDING WARNING: Loan purpose is securities purchase. "
            "Verify Regulation U compliance -- non-purpose loans cannot "
            "be used to buy margin stock."
        )
