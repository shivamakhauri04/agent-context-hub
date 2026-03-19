"""Tests for custodial account (UTMA/UGMA) checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.custodial import check_custodial


def test_prohibited_options_critical() -> None:
    """Options in custodial account -> CRITICAL."""
    portfolio = {
        "custodial_config": {
            "is_custodial": True,
            "minor_age": 12,
            "state_age_of_majority": 18,
            "unearned_income_ytd": 500,
            "has_options": True,
            "has_margin": False,
            "has_futures": False,
            "has_short_positions": False,
        },
    }
    violations = check_custodial(portfolio)
    assert any("CRITICAL" in v and "options" in v for v in violations)


def test_prohibited_multiple_instruments() -> None:
    """Multiple prohibited instruments -> single CRITICAL listing all."""
    portfolio = {
        "custodial_config": {
            "is_custodial": True,
            "minor_age": 10,
            "state_age_of_majority": 18,
            "unearned_income_ytd": 0,
            "has_options": True,
            "has_margin": True,
            "has_futures": True,
            "has_short_positions": True,
        },
    }
    violations = check_custodial(portfolio)
    critical = [v for v in violations if "CRITICAL" in v]
    assert len(critical) == 1
    assert "options" in critical[0] and "margin" in critical[0]


def test_kiddie_tax_warning() -> None:
    """Unearned income > $2,600 -> WARNING."""
    portfolio = {
        "custodial_config": {
            "is_custodial": True,
            "minor_age": 14,
            "state_age_of_majority": 18,
            "unearned_income_ytd": 3500,
            "has_options": False,
            "has_margin": False,
            "has_futures": False,
            "has_short_positions": False,
        },
    }
    violations = check_custodial(portfolio)
    assert any("WARNING" in v and "kiddie tax" in v for v in violations)


def test_approaching_majority_info() -> None:
    """Minor age = majority - 1 -> INFO."""
    portfolio = {
        "custodial_config": {
            "is_custodial": True,
            "minor_age": 17,
            "state_age_of_majority": 18,
            "unearned_income_ytd": 500,
            "has_options": False,
            "has_margin": False,
            "has_futures": False,
            "has_short_positions": False,
        },
    }
    violations = check_custodial(portfolio)
    assert any("INFO" in v and "age of majority" in v for v in violations)


def test_clean_custodial_no_violations() -> None:
    """Clean custodial account -> pass."""
    portfolio = {
        "custodial_config": {
            "is_custodial": True,
            "minor_age": 10,
            "state_age_of_majority": 18,
            "unearned_income_ytd": 1000,
            "has_options": False,
            "has_margin": False,
            "has_futures": False,
            "has_short_positions": False,
        },
    }
    violations = check_custodial(portfolio)
    assert violations == []


def test_not_custodial_skips() -> None:
    """is_custodial=False -> skip."""
    portfolio = {
        "custodial_config": {
            "is_custodial": False,
            "minor_age": 5,
            "has_options": True,
        },
    }
    violations = check_custodial(portfolio)
    assert violations == []


def test_skip_when_config_absent() -> None:
    """No custodial_config -> skip."""
    portfolio = {"equity": 50000}
    violations = check_custodial(portfolio)
    assert violations == []


def test_checker_registered() -> None:
    """'custodial' should be in _RULE_CHECKERS."""
    assert "custodial" in _RULE_CHECKERS
    assert _RULE_CHECKERS["custodial"] is check_custodial
