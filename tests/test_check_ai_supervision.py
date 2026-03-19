"""Tests for AI agent supervision compliance checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.ai_supervision import check_ai_supervision


def test_missing_disclaimer_critical() -> None:
    """AI content without risk disclaimer -> CRITICAL."""
    portfolio = {
        "ai_supervision_config": {
            "is_ai_generated": True,
            "has_risk_disclaimer": False,
            "contains_return_prediction": False,
            "suitability_check_completed": True,
            "interaction_logged": True,
            "model_version_tracked": True,
            "supervisory_review_enabled": True,
        },
    }
    violations = check_ai_supervision(portfolio)
    assert any("CRITICAL" in v and "disclaimer" in v for v in violations)


def test_return_prediction_critical() -> None:
    """AI content with return prediction -> CRITICAL."""
    portfolio = {
        "ai_supervision_config": {
            "is_ai_generated": True,
            "has_risk_disclaimer": True,
            "contains_return_prediction": True,
            "suitability_check_completed": True,
            "interaction_logged": True,
            "model_version_tracked": True,
            "supervisory_review_enabled": True,
        },
    }
    violations = check_ai_supervision(portfolio)
    assert any("CRITICAL" in v and "prediction" in v for v in violations)


def test_no_suitability_warning() -> None:
    """AI recommendation without suitability check -> WARNING."""
    portfolio = {
        "ai_supervision_config": {
            "is_ai_generated": True,
            "has_risk_disclaimer": True,
            "contains_return_prediction": False,
            "suitability_check_completed": False,
            "interaction_logged": True,
            "model_version_tracked": True,
            "supervisory_review_enabled": True,
        },
    }
    violations = check_ai_supervision(portfolio)
    assert any("WARNING" in v and "suitability" in v for v in violations)


def test_no_record_retention_warning() -> None:
    """Interaction not logged -> WARNING."""
    portfolio = {
        "ai_supervision_config": {
            "is_ai_generated": True,
            "has_risk_disclaimer": True,
            "contains_return_prediction": False,
            "suitability_check_completed": True,
            "interaction_logged": False,
            "model_version_tracked": False,
            "supervisory_review_enabled": True,
        },
    }
    violations = check_ai_supervision(portfolio)
    assert any("WARNING" in v and "logged" in v for v in violations)
    assert any("WARNING" in v and "Model version" in v for v in violations)


def test_no_supervisory_review_warning() -> None:
    """Review disabled -> WARNING."""
    portfolio = {
        "ai_supervision_config": {
            "is_ai_generated": True,
            "has_risk_disclaimer": True,
            "contains_return_prediction": False,
            "suitability_check_completed": True,
            "interaction_logged": True,
            "model_version_tracked": True,
            "supervisory_review_enabled": False,
        },
    }
    violations = check_ai_supervision(portfolio)
    assert any("WARNING" in v and "Supervisory review" in v for v in violations)


def test_all_compliant_no_violations() -> None:
    """Fully compliant AI config -> pass."""
    portfolio = {
        "ai_supervision_config": {
            "is_ai_generated": True,
            "has_risk_disclaimer": True,
            "contains_return_prediction": False,
            "suitability_check_completed": True,
            "interaction_logged": True,
            "model_version_tracked": True,
            "supervisory_review_enabled": True,
        },
    }
    violations = check_ai_supervision(portfolio)
    assert violations == []


def test_not_ai_generated_skips() -> None:
    """is_ai_generated=False -> skip all checks."""
    portfolio = {
        "ai_supervision_config": {
            "is_ai_generated": False,
            "has_risk_disclaimer": False,
            "contains_return_prediction": True,
        },
    }
    violations = check_ai_supervision(portfolio)
    assert violations == []


def test_skip_when_config_absent() -> None:
    """No ai_supervision_config -> skip."""
    portfolio = {"equity": 100000}
    violations = check_ai_supervision(portfolio)
    assert violations == []


def test_checker_registered() -> None:
    """'ai-supervision' should be in _RULE_CHECKERS."""
    assert "ai-supervision" in _RULE_CHECKERS
    assert _RULE_CHECKERS["ai-supervision"] is check_ai_supervision
