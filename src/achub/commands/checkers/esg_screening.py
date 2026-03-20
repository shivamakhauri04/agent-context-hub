"""ESG screening compliance checker."""
from __future__ import annotations


def check_esg_screening(portfolio: dict) -> list[str]:
    """Check ESG screening compliance rules.

    Skips if ``esg_config`` is absent.  Flags:
    - CRITICAL if ESG fund holds excluded sector positions (greenwashing)
    - CRITICAL if ERISA account uses ESG exclusions without financial materiality
    - WARNING if ESG enabled but rating provider not disclosed
    - WARNING if ESG exclusions cause tracking error above cap
    - WARNING if position labeled ESG but score < 50
    """
    violations: list[str] = []

    config = portfolio.get("esg_config")
    if not config:
        return violations

    if not config.get("esg_enabled", False):
        return violations

    for pos in config.get("esg_positions", []):
        if pos.get("holds_excluded_sectors", False):
            symbol = pos.get("symbol", "UNKNOWN")
            violations.append(
                f"ESG CRITICAL: {symbol} holds excluded sector positions "
                f"despite ESG label -- potential greenwashing violation."
            )

    if config.get("is_erisa_account", False):
        violations.append(
            "ESG CRITICAL: ERISA account using ESG exclusions -- "
            "ESG criteria must demonstrate financial materiality "
            "under DOL fiduciary rules for ERISA plans."
        )

    if not config.get("provider_disclosed", False):
        violations.append(
            "ESG WARNING: ESG screening enabled but rating provider "
            "is not disclosed -- clients must know which ESG methodology is used."
        )

    tracking_error = config.get("tracking_error_pct", 0)
    tracking_cap = config.get("tracking_error_cap_pct", 0)
    if tracking_cap > 0 and tracking_error > tracking_cap:
        violations.append(
            f"ESG WARNING: ESG exclusions cause {tracking_error:.1f}% tracking "
            f"error, exceeding {tracking_cap:.1f}% cap -- exclusions may be "
            f"too aggressive for benchmark-relative performance."
        )

    for pos in config.get("esg_positions", []):
        score = pos.get("esg_score", 100)
        label = pos.get("esg_label", "")
        if label and score < 50:
            symbol = pos.get("symbol", "UNKNOWN")
            violations.append(
                f"ESG WARNING: {symbol} labeled '{label}' but ESG score "
                f"is {score} (below 50) -- label may be misleading."
            )

    return violations
