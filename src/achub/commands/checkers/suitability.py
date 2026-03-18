"""Suitability / know-your-customer checker."""
from __future__ import annotations


def check_suitability(portfolio: dict) -> list[str]:
    """Check suitability of strategies and positions.

    Skips if no ``pending_strategies`` and no ``positions``.  Flags:
    - CRITICAL if strategy risk exceeds customer tolerance
    - WARNING if strategy complexity exceeds customer experience
    - CRITICAL if annual turnover ratio suggests churning
    - WARNING if cost-to-equity ratio is excessive
    - WARNING if single position exceeds 25% concentration
    - CRITICAL if pending strategies but no risk tolerance profile
    """
    violations: list[str] = []
    strategies = portfolio.get("pending_strategies", [])
    positions = portfolio.get("positions", [])
    has_metrics = (
        portfolio.get("turnover_ratio_annual") is not None
        or portfolio.get("cost_equity_ratio_annual") is not None
    )

    if not strategies and not positions and not has_metrics:
        return violations

    tolerance = portfolio.get("customer_risk_tolerance")
    experience = portfolio.get("customer_experience_level", 5)

    if strategies and tolerance is None:
        violations.append(
            "SUITABILITY CRITICAL: Pending strategies require customer "
            "risk tolerance profile -- missing customer_risk_tolerance."
        )

    _check_strategies(strategies, tolerance, experience, violations)
    _check_trading_metrics(portfolio, violations)
    _check_concentration(positions, portfolio, violations)

    return violations


def _check_strategies(
    strategies: list[dict],
    tolerance: int | None,
    experience: int,
    violations: list[str],
) -> None:
    for s in strategies:
        name = s.get("strategy", s.get("name", "unknown"))
        symbol = s.get("symbol", "")
        risk = s.get("risk_level", 0)
        complexity = s.get("complexity", 1)

        if tolerance is not None and risk > tolerance:
            violations.append(
                f"SUITABILITY CRITICAL: Strategy '{name}' for {symbol} "
                f"has risk level {risk} but customer tolerance is "
                f"{tolerance} -- unsuitable recommendation."
            )
        if complexity > experience:
            violations.append(
                f"SUITABILITY WARNING: Strategy '{name}' complexity "
                f"{complexity} exceeds customer experience level "
                f"{experience} -- may be unsuitable."
            )


def _check_trading_metrics(
    portfolio: dict, violations: list[str]
) -> None:
    turnover = portfolio.get("turnover_ratio_annual", 0)
    if turnover > 6:
        violations.append(
            f"SUITABILITY CRITICAL: Annual turnover ratio {turnover:.1f} "
            f"exceeds 6.0 -- potential churning violation "
            f"(FINRA Rule 2111)."
        )

    cost_ratio = portfolio.get("cost_equity_ratio_annual", 0)
    if cost_ratio > 0.20:
        violations.append(
            f"SUITABILITY WARNING: Annual cost-to-equity ratio "
            f"{cost_ratio:.2f} exceeds 0.20 -- excessive trading costs."
        )


def _check_concentration(
    positions: list[dict], portfolio: dict, violations: list[str]
) -> None:
    equity = portfolio.get("equity", 0)
    if equity <= 0:
        return
    for pos in positions:
        qty = pos.get("quantity", 0)
        price = pos.get("current_price", 0)
        value = qty * price
        pct = value / equity
        if pct > 0.25:
            symbol = pos.get("symbol", "unknown")
            violations.append(
                f"SUITABILITY WARNING: {symbol} is {pct * 100:.0f}% of "
                f"portfolio (${value:,.0f} / ${equity:,.0f}) -- single "
                f"position exceeds 25% concentration limit."
            )
