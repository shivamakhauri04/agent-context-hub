"""AI agent supervision compliance checker."""
from __future__ import annotations


def check_ai_supervision(portfolio: dict) -> list[str]:
    """Check AI supervision compliance: disclaimers, predictions, records, review.

    Skips when ``ai_supervision_config`` is absent.  Flags:
    - CRITICAL if AI-generated content lacks risk disclaimer
    - CRITICAL if AI-generated content contains return prediction
    - WARNING if AI recommendation issued without suitability check
    - WARNING if interaction not logged or model version not tracked
    - WARNING if supervisory review is disabled
    """
    violations: list[str] = []
    config = portfolio.get("ai_supervision_config")
    if not config:
        return violations

    if not config.get("is_ai_generated", False):
        return violations

    # 1. No risk disclaimer
    if not config.get("has_risk_disclaimer", False):
        violations.append(
            "AI SUPERVISION CRITICAL: AI-generated investment content "
            "missing required risk disclaimer (FINRA Rule 2210)."
        )

    # 2. Return prediction
    if config.get("contains_return_prediction", False):
        violations.append(
            "AI SUPERVISION CRITICAL: AI-generated content contains "
            "return prediction or guarantee — prohibited under Rule 2210."
        )

    # 3. Suitability not done
    if not config.get("suitability_check_completed", False):
        violations.append(
            "AI SUPERVISION WARNING: AI recommendation issued without "
            "suitability/Reg BI analysis."
        )

    # 4. Record retention
    if not config.get("interaction_logged", False):
        violations.append(
            "AI SUPERVISION WARNING: AI interaction not logged — "
            "required for 3+ year retention under FINRA Rule 4511."
        )
    if not config.get("model_version_tracked", False):
        violations.append(
            "AI SUPERVISION WARNING: Model version not tracked — "
            "required for audit trail."
        )

    # 5. Supervisory review
    if not config.get("supervisory_review_enabled", False):
        violations.append(
            "AI SUPERVISION WARNING: Supervisory review disabled — "
            "FINRA Rule 3110 requires supervision of AI communications."
        )

    return violations
