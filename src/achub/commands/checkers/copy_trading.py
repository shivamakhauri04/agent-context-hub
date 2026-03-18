"""Copy trading checker."""
from __future__ import annotations


def check_copy_trading(portfolio: dict) -> list[str]:
    """Check copy trading configuration for suitability issues.

    Skips if no ``copy_trading_config``.  Flags:
    - CRITICAL if leader risk level exceeds customer risk tolerance
    - WARNING if copy allocation exceeds 25% of equity
    - WARNING if copier/leader size ratio causes rounding distortion
    - WARNING if IRA account copies a leader using margin or options
    """
    violations: list[str] = []
    config = portfolio.get("copy_trading_config")

    if not config:
        return violations

    _check_risk_mismatch(portfolio, config, violations)
    _check_concentration(portfolio, config, violations)
    _check_size_ratio(config, violations)
    _check_ira_prohibited_strategies(portfolio, config, violations)

    return violations


def _check_risk_mismatch(
    portfolio: dict, config: dict, violations: list[str]
) -> None:
    leader_risk = config.get("leader_risk_level", 0)
    customer_risk = portfolio.get("customer_risk_tolerance", 5)
    if leader_risk > customer_risk:
        violations.append(
            f"COPY TRADING CRITICAL: Leader risk level {leader_risk} "
            f"exceeds customer risk tolerance {customer_risk}. "
            f"Strategy is unsuitable for this investor."
        )


def _check_concentration(
    portfolio: dict, config: dict, violations: list[str]
) -> None:
    equity = portfolio.get("equity", 0)
    allocation = config.get("copy_allocation_usd", 0)
    if equity > 0 and allocation / equity > 0.25:
        pct = allocation / equity * 100
        violations.append(
            f"COPY TRADING WARNING: Copy allocation ${allocation:,.0f} "
            f"is {pct:.0f}% of equity -- exceeds 25% concentration limit "
            f"for a single leader."
        )


def _check_size_ratio(
    config: dict, violations: list[str]
) -> None:
    leader_size = config.get("leader_portfolio_size", 0)
    allocation = config.get("copy_allocation_usd", 0)
    if leader_size > 0 and allocation > 0:
        ratio = leader_size / allocation
        if ratio > 100:
            violations.append(
                f"COPY TRADING WARNING: Leader portfolio is {ratio:.0f}x "
                f"larger than copy allocation -- fractional-share rounding "
                f"will cause significant tracking distortion."
            )


def _check_ira_prohibited_strategies(
    portfolio: dict, config: dict, violations: list[str]
) -> None:
    ira_type = portfolio.get("ira_type")
    if not ira_type:
        return
    uses_margin = config.get("leader_uses_margin", False)
    uses_options = config.get("leader_uses_options", False)
    if uses_margin or uses_options:
        strategies = []
        if uses_margin:
            strategies.append("margin")
        if uses_options:
            strategies.append("options")
        violations.append(
            f"COPY TRADING WARNING: IRA account cannot replicate leader's "
            f"{', '.join(strategies)} strategies. Returns will diverge "
            f"from leader."
        )
