"""Tests for IRA compliance checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.ira import check_ira_compliance

# --- Contribution limit tests ---


def test_ira_over_contribution_under_50() -> None:
    """YTD=$7,500, age=35 -> CRITICAL (exceeds $7k limit)."""
    portfolio = {"ira_type": "traditional", "ira_contribution_ytd": 7500, "account_holder_age": 35}
    violations = check_ira_compliance(portfolio)
    assert len(violations) == 1
    assert "CRITICAL" in violations[0]
    assert "excise tax" in violations[0].lower()


def test_ira_over_contribution_over_50() -> None:
    """YTD=$8,500, age=55 -> CRITICAL (exceeds $8k catch-up limit)."""
    portfolio = {"ira_type": "traditional", "ira_contribution_ytd": 8500, "account_holder_age": 55}
    violations = check_ira_compliance(portfolio)
    assert len(violations) == 1
    assert "CRITICAL" in violations[0]
    assert "catch-up" in violations[0].lower()


def test_ira_within_limit() -> None:
    """YTD=$5,000, age=35 -> pass."""
    portfolio = {"ira_type": "traditional", "ira_contribution_ytd": 5000, "account_holder_age": 35}
    violations = check_ira_compliance(portfolio)
    assert violations == []


def test_ira_approaching_limit() -> None:
    """YTD=$6,500, age=35 -> WARNING (above 90% of $7k)."""
    portfolio = {"ira_type": "traditional", "ira_contribution_ytd": 6500, "account_holder_age": 35}
    violations = check_ira_compliance(portfolio)
    assert len(violations) == 1
    assert "WARNING" in violations[0]
    assert "90%" in violations[0]


# --- Roth income eligibility tests ---


def test_roth_income_exceeded_single() -> None:
    """MAGI=$170k, single -> CRITICAL (above $165k upper limit)."""
    portfolio = {
        "ira_type": "roth",
        "ira_contribution_ytd": 1000,
        "account_holder_age": 35,
        "magi": 170000,
        "filing_status": "single",
    }
    violations = check_ira_compliance(portfolio)
    assert any("CRITICAL" in v and "Roth" in v for v in violations)


def test_roth_income_phaseout_single() -> None:
    """MAGI=$155k, single -> WARNING (in phase-out range)."""
    portfolio = {
        "ira_type": "roth",
        "ira_contribution_ytd": 1000,
        "account_holder_age": 35,
        "magi": 155000,
        "filing_status": "single",
    }
    violations = check_ira_compliance(portfolio)
    assert any("WARNING" in v and "phase-out" in v for v in violations)


def test_roth_income_eligible() -> None:
    """MAGI=$100k -> pass (well below phase-out)."""
    portfolio = {
        "ira_type": "roth",
        "ira_contribution_ytd": 1000,
        "account_holder_age": 35,
        "magi": 100000,
        "filing_status": "single",
    }
    violations = check_ira_compliance(portfolio)
    assert violations == []


def test_roth_income_exceeded_mfj() -> None:
    """MAGI=$250k, MFJ -> CRITICAL (above $246k upper limit)."""
    portfolio = {
        "ira_type": "roth",
        "ira_contribution_ytd": 1000,
        "account_holder_age": 35,
        "magi": 250000,
        "filing_status": "married_filing_jointly",
    }
    violations = check_ira_compliance(portfolio)
    assert any("CRITICAL" in v and "Roth" in v for v in violations)


# --- Early withdrawal tests ---


def test_early_withdrawal_under_59() -> None:
    """Withdrawal=$5k, age=45 -> WARNING (10% penalty)."""
    portfolio = {
        "ira_type": "traditional",
        "ira_contribution_ytd": 0,
        "account_holder_age": 45,
        "withdrawal_amount": 5000,
    }
    violations = check_ira_compliance(portfolio)
    assert any("WARNING" in v and "penalty" in v.lower() for v in violations)


def test_withdrawal_over_59() -> None:
    """Withdrawal=$5k, age=62 -> pass."""
    portfolio = {
        "ira_type": "traditional",
        "ira_contribution_ytd": 0,
        "account_holder_age": 62,
        "withdrawal_amount": 5000,
    }
    violations = check_ira_compliance(portfolio)
    assert violations == []


# --- Non-IRA skip test ---


def test_non_ira_account_skips() -> None:
    """No ira_type -> checker skips entirely."""
    portfolio = {"account_type": "margin", "equity": 50000}
    violations = check_ira_compliance(portfolio)
    assert violations == []


# --- Registration test ---


def test_ira_checker_registered() -> None:
    """Verify 'ira' is in _RULE_CHECKERS and points to check_ira_compliance."""
    assert "ira" in _RULE_CHECKERS
    assert _RULE_CHECKERS["ira"] is check_ira_compliance
