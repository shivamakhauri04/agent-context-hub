"""Options approval level checker."""
from __future__ import annotations

# Strategy name -> minimum approval level required
_STRATEGY_LEVELS: dict[str, int] = {
    "covered_call": 1,
    "protective_put": 1,
    "long_call": 2,
    "long_put": 2,
    "debit_spread": 3,
    "credit_spread": 3,
    "iron_condor": 3,
    "butterfly": 3,
    "naked_put": 4,
    "naked_call": 5,
}


def check_options_approval(portfolio: dict) -> list[str]:
    """Check options approval level against pending strategies.

    Reads ``options_approval_level`` (default 0), ``pending_options_strategies``
    (list of dicts with ``strategy`` and ``symbol`` keys), and
    ``expiring_options`` (list of dicts with ``exercise_cost`` key) from the
    portfolio.  Returns a list of violation strings.
    """
    violations: list[str] = []
    account_level = portfolio.get("options_approval_level", 0)
    pending = portfolio.get("pending_options_strategies", [])

    for entry in pending:
        strategy = entry.get("strategy", "").lower()
        symbol = entry.get("symbol", "???")
        required = _STRATEGY_LEVELS.get(strategy)

        if required is None:
            violations.append(
                f"OPTIONS VIOLATION: Unknown strategy '{strategy}' for "
                f"{symbol} — cannot verify approval level."
            )
            continue

        if account_level < required:
            violations.append(
                f"OPTIONS VIOLATION: {symbol} strategy '{strategy}' requires "
                f"Level {required} approval, account has Level {account_level}."
            )

    # Check expiring ITM options for capital sufficiency
    cash = portfolio.get("cash", 0)
    expiring = portfolio.get("expiring_options", [])
    for opt in expiring:
        exercise_cost = opt.get("exercise_cost", 0)
        symbol = opt.get("symbol", "???")
        if exercise_cost > cash:
            violations.append(
                f"OPTIONS WARNING: {symbol} expiring ITM, exercise cost "
                f"${exercise_cost:,.0f} exceeds cash ${cash:,.0f}."
            )

    return violations
