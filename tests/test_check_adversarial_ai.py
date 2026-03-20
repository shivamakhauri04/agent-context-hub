"""Tests for adversarial AI / prompt injection checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.adversarial_ai import check_adversarial_ai


def test_adversarial_no_config_skips() -> None:
    """No adversarial_ai_config -> skip."""
    portfolio = {"account_type": "margin", "equity": 50000}
    assert check_adversarial_ai(portfolio) == []


def test_adversarial_system_override_critical() -> None:
    """System override attempt -> CRITICAL."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": True,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": False,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert any("CRITICAL" in v and "System override" in v for v in violations)


def test_adversarial_data_exfiltration_critical() -> None:
    """Data exfiltration pattern -> CRITICAL."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": True,
            "model_output_contains_pii": False,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert any("CRITICAL" in v and "exfiltration" in v for v in violations)


def test_adversarial_pii_in_output_critical() -> None:
    """PII in model output -> CRITICAL."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": True,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert any("CRITICAL" in v and "PII" in v for v in violations)


def test_adversarial_no_sanitization_warning() -> None:
    """Input sanitization disabled -> WARNING."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": False,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": False,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert any("WARNING" in v and "sanitization" in v for v in violations)


def test_adversarial_no_output_validation_warning() -> None:
    """Output validation disabled -> WARNING."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": False,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": False,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert any("WARNING" in v and "Output validation" in v for v in violations)


def test_adversarial_no_injection_scan_warning() -> None:
    """Prompt injection scanning disabled -> WARNING."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": False,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": False,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert any("WARNING" in v and "injection scanning" in v for v in violations)


def test_adversarial_no_rate_limit_and_no_escalation_warning() -> None:
    """Both rate limit and human escalation disabled -> WARNING."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": False,
            "rate_limit_enabled": False,
            "human_escalation_available": False,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert any("WARNING" in v and "rate limiting" in v for v in violations)


def test_adversarial_rate_limit_only_no_warning() -> None:
    """Rate limit enabled but no escalation -> no combined warning."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": False,
            "rate_limit_enabled": True,
            "human_escalation_available": False,
        },
    }
    violations = check_adversarial_ai(portfolio)
    assert not any("rate limiting" in v for v in violations)


def test_adversarial_all_clean() -> None:
    """Fully compliant config -> no violations."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": False,
            "contains_data_exfiltration_pattern": False,
            "model_output_contains_pii": False,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    assert check_adversarial_ai(portfolio) == []


def test_adversarial_multiple_criticals() -> None:
    """Multiple attack patterns -> multiple CRITICALs."""
    portfolio = {
        "adversarial_ai_config": {
            "input_sanitization_enabled": True,
            "output_validation_enabled": True,
            "prompt_injection_scan_enabled": True,
            "contains_system_override_attempt": True,
            "contains_data_exfiltration_pattern": True,
            "model_output_contains_pii": True,
            "rate_limit_enabled": True,
            "human_escalation_available": True,
        },
    }
    violations = check_adversarial_ai(portfolio)
    critical_count = sum(1 for v in violations if "CRITICAL" in v)
    assert critical_count == 3


def test_adversarial_checker_registered() -> None:
    """'adversarial-ai' should be in _RULE_CHECKERS."""
    assert "adversarial-ai" in _RULE_CHECKERS
    assert _RULE_CHECKERS["adversarial-ai"] is check_adversarial_ai
