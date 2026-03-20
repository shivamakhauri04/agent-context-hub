"""Tests for ESG screening compliance checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.esg_screening import check_esg_screening


def test_esg_no_config_skips() -> None:
    """No esg_config -> skip."""
    portfolio = {"account_type": "margin", "equity": 50000}
    assert check_esg_screening(portfolio) == []


def test_esg_disabled_skips() -> None:
    """ESG not enabled -> skip."""
    portfolio = {
        "esg_config": {
            "esg_enabled": False,
            "provider_disclosed": False,
        },
    }
    assert check_esg_screening(portfolio) == []


def test_esg_greenwashing_critical() -> None:
    """ESG fund holds excluded sectors -> CRITICAL."""
    portfolio = {
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": True,
            "esg_positions": [
                {"symbol": "ESGU", "esg_score": 75, "esg_label": "ESG Leader",
                 "holds_excluded_sectors": True},
            ],
            "tracking_error_pct": 1.0,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": False,
        },
    }
    violations = check_esg_screening(portfolio)
    assert any("CRITICAL" in v and "greenwashing" in v for v in violations)


def test_esg_erisa_conflict_critical() -> None:
    """ERISA account with ESG exclusions -> CRITICAL."""
    portfolio = {
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": True,
            "esg_positions": [],
            "tracking_error_pct": 0.5,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": True,
        },
    }
    violations = check_esg_screening(portfolio)
    assert any("CRITICAL" in v and "ERISA" in v for v in violations)


def test_esg_provider_undisclosed_warning() -> None:
    """ESG enabled but provider not disclosed -> WARNING."""
    portfolio = {
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": False,
            "esg_positions": [],
            "tracking_error_pct": 0.5,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": False,
        },
    }
    violations = check_esg_screening(portfolio)
    assert any("WARNING" in v and "provider" in v for v in violations)


def test_esg_tracking_error_exceeds_cap_warning() -> None:
    """Tracking error above cap -> WARNING."""
    portfolio = {
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": True,
            "esg_positions": [],
            "tracking_error_pct": 3.5,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": False,
        },
    }
    violations = check_esg_screening(portfolio)
    assert any("WARNING" in v and "tracking error" in v for v in violations)


def test_esg_low_score_with_label_warning() -> None:
    """Position labeled ESG but score < 50 -> WARNING."""
    portfolio = {
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": True,
            "esg_positions": [
                {"symbol": "XYZ", "esg_score": 35, "esg_label": "Sustainable",
                 "holds_excluded_sectors": False},
            ],
            "tracking_error_pct": 1.0,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": False,
        },
    }
    violations = check_esg_screening(portfolio)
    assert any("WARNING" in v and "below 50" in v for v in violations)


def test_esg_high_score_no_warning() -> None:
    """Position with ESG label and score >= 50 -> no low-score warning."""
    portfolio = {
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": True,
            "esg_positions": [
                {"symbol": "ESGU", "esg_score": 80, "esg_label": "ESG Leader",
                 "holds_excluded_sectors": False},
            ],
            "tracking_error_pct": 1.0,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": False,
        },
    }
    violations = check_esg_screening(portfolio)
    assert not any("below 50" in v for v in violations)


def test_esg_all_clean() -> None:
    """Fully compliant ESG config -> no violations."""
    portfolio = {
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": True,
            "esg_positions": [
                {"symbol": "ESGU", "esg_score": 80, "esg_label": "ESG Leader",
                 "holds_excluded_sectors": False},
            ],
            "tracking_error_pct": 1.0,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": False,
        },
    }
    assert check_esg_screening(portfolio) == []


def test_esg_checker_registered() -> None:
    """'esg-screening' should be in _RULE_CHECKERS."""
    assert "esg-screening" in _RULE_CHECKERS
    assert _RULE_CHECKERS["esg-screening"] is check_esg_screening
