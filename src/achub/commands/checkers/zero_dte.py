"""0DTE (zero days to expiration) options checker."""
from __future__ import annotations

_DEFAULT_MAX_PORTFOLIO_PCT = 0.05  # 5% default max allocation


def check_zero_dte(portfolio: dict) -> list[str]:
    """Check 0DTE options position risk.

    Skips if no ``zero_dte_positions``.  Flags:
    - CRITICAL if any short position exercise cost exceeds equity
    - WARNING if total max loss exceeds portfolio allocation limit
    - WARNING if options approval level < 3 with short 0DTE positions
    - CAUTION if any single position max loss > 2% of equity
    """
    violations: list[str] = []
    positions = portfolio.get("zero_dte_positions", [])

    if not positions:
        return violations

    equity = portfolio.get("equity", 0)
    max_pct = portfolio.get("zero_dte_max_portfolio_pct", _DEFAULT_MAX_PORTFOLIO_PCT)
    approval_level = portfolio.get("options_approval_level", 0)

    total_max_loss = 0.0
    has_short = False

    for pos in positions:
        symbol = pos.get("symbol", "???")
        direction = pos.get("direction", "long")
        exercise_cost = pos.get("exercise_cost", 0)
        max_loss = pos.get("max_loss", 0)
        total_max_loss += max_loss

        if direction == "short":
            has_short = True
            if exercise_cost > equity:
                violations.append(
                    f"0DTE CRITICAL: {symbol} short exercise cost "
                    f"${exercise_cost:,.0f} exceeds account equity "
                    f"${equity:,.0f}."
                )

        if equity > 0 and max_loss > equity * 0.02:
            violations.append(
                f"0DTE CAUTION: {symbol} max loss ${max_loss:,.0f} exceeds "
                f"2% of equity (${equity * 0.02:,.0f})."
            )

    if equity > 0 and total_max_loss > equity * max_pct:
        violations.append(
            f"0DTE WARNING: Total 0DTE risk ${total_max_loss:,.0f} exceeds "
            f"{max_pct:.0%} portfolio limit (${equity * max_pct:,.0f})."
        )

    if has_short and approval_level < 3:
        violations.append(
            f"0DTE WARNING: Short 0DTE positions require options approval "
            f"level 3+, account has level {approval_level}."
        )

    return violations
