"""Adversarial AI / prompt injection compliance checker."""
from __future__ import annotations


def check_adversarial_ai(portfolio: dict) -> list[str]:
    """Check adversarial AI security controls.

    Skips if ``adversarial_ai_config`` is absent.  Flags:
    - CRITICAL if system override attempt detected in input
    - CRITICAL if data exfiltration pattern detected
    - CRITICAL if model output contains PII
    - WARNING if input sanitization is disabled
    - WARNING if output validation is disabled
    - WARNING if prompt injection scanning is disabled
    - WARNING if both rate limiting and human escalation are disabled
    """
    violations: list[str] = []

    config = portfolio.get("adversarial_ai_config")
    if not config:
        return violations

    if config.get("contains_system_override_attempt", False):
        violations.append(
            "ADVERSARIAL CRITICAL: System override attempt detected in "
            "user input -- potential prompt injection attack."
        )

    if config.get("contains_data_exfiltration_pattern", False):
        violations.append(
            "ADVERSARIAL CRITICAL: Data exfiltration pattern detected "
            "-- input may attempt to extract sensitive information."
        )

    if config.get("model_output_contains_pii", False):
        violations.append(
            "ADVERSARIAL CRITICAL: Model output contains PII "
            "(personally identifiable information) -- output must be "
            "filtered before delivery to user."
        )

    if not config.get("input_sanitization_enabled", True):
        violations.append(
            "ADVERSARIAL WARNING: Input sanitization is disabled "
            "-- all user-facing AI inputs must be sanitized per "
            "FINRA 2026 adversarial AI guidance."
        )

    if not config.get("output_validation_enabled", True):
        violations.append(
            "ADVERSARIAL WARNING: Output validation is disabled "
            "-- AI outputs must be validated to filter PII, account "
            "numbers, and credentials."
        )

    if not config.get("prompt_injection_scan_enabled", True):
        violations.append(
            "ADVERSARIAL WARNING: Prompt injection scanning is disabled "
            "-- system override attempts will not be detected."
        )

    rate_limit = config.get("rate_limit_enabled", True)
    human_escalation = config.get("human_escalation_available", True)
    if not rate_limit and not human_escalation:
        violations.append(
            "ADVERSARIAL WARNING: Both rate limiting and human escalation "
            "are disabled -- at least one safeguard must be active for "
            "AI interaction oversight."
        )

    return violations
