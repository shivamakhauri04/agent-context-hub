"""Tests for trust accounts compliance checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.trust_accounts import check_trust_accounts


def test_trust_no_config_skips() -> None:
    """No trust_config -> skip."""
    portfolio = {"account_type": "margin", "equity": 50000}
    assert check_trust_accounts(portfolio) == []


def test_trust_not_trust_account_skips() -> None:
    """trust_config present but is_trust_account=False -> skip."""
    portfolio = {
        "trust_config": {
            "is_trust_account": False,
            "trust_type": "revocable",
        },
    }
    assert check_trust_accounts(portfolio) == []


def test_trust_self_dealing_critical() -> None:
    """Self-dealing transaction -> CRITICAL."""
    portfolio = {
        "trust_config": {
            "is_trust_account": True,
            "trust_type": "irrevocable",
            "trust_assets_usd": 5000000,
            "estate_tax_exclusion_usd": 13610000,
            "trustee_is_beneficiary": False,
            "has_self_dealing_transaction": True,
            "annual_distribution_pct": 4,
            "generation_skipping_transfer": False,
            "gst_exemption_used_usd": 0,
        },
    }
    violations = check_trust_accounts(portfolio)
    assert any("CRITICAL" in v and "Self-dealing" in v for v in violations)


def test_trust_estate_tax_exposure_critical() -> None:
    """Trust assets > exclusion -> CRITICAL."""
    portfolio = {
        "trust_config": {
            "is_trust_account": True,
            "trust_type": "irrevocable",
            "trust_assets_usd": 15000000,
            "estate_tax_exclusion_usd": 13610000,
            "trustee_is_beneficiary": False,
            "has_self_dealing_transaction": False,
            "annual_distribution_pct": 4,
            "generation_skipping_transfer": False,
            "gst_exemption_used_usd": 0,
        },
    }
    violations = check_trust_accounts(portfolio)
    assert any("CRITICAL" in v and "estate tax" in v for v in violations)


def test_trust_trustee_beneficiary_conflict_warning() -> None:
    """Irrevocable trust with trustee as beneficiary -> WARNING."""
    portfolio = {
        "trust_config": {
            "is_trust_account": True,
            "trust_type": "irrevocable",
            "trust_assets_usd": 5000000,
            "estate_tax_exclusion_usd": 13610000,
            "trustee_is_beneficiary": True,
            "has_self_dealing_transaction": False,
            "annual_distribution_pct": 4,
            "generation_skipping_transfer": False,
            "gst_exemption_used_usd": 0,
        },
    }
    violations = check_trust_accounts(portfolio)
    assert any("WARNING" in v and "beneficiary" in v for v in violations)


def test_trust_gst_no_exemption_tracking_warning() -> None:
    """GST enabled but no exemption used -> WARNING."""
    portfolio = {
        "trust_config": {
            "is_trust_account": True,
            "trust_type": "irrevocable",
            "trust_assets_usd": 5000000,
            "estate_tax_exclusion_usd": 13610000,
            "trustee_is_beneficiary": False,
            "has_self_dealing_transaction": False,
            "annual_distribution_pct": 4,
            "generation_skipping_transfer": True,
            "gst_exemption_used_usd": 0,
        },
    }
    violations = check_trust_accounts(portfolio)
    assert any("WARNING" in v and "GST" in v for v in violations)


def test_trust_unsustainable_distribution_warning() -> None:
    """Distribution rate > 7% -> WARNING."""
    portfolio = {
        "trust_config": {
            "is_trust_account": True,
            "trust_type": "irrevocable",
            "trust_assets_usd": 5000000,
            "estate_tax_exclusion_usd": 13610000,
            "trustee_is_beneficiary": False,
            "has_self_dealing_transaction": False,
            "annual_distribution_pct": 8.5,
            "generation_skipping_transfer": False,
            "gst_exemption_used_usd": 0,
        },
    }
    violations = check_trust_accounts(portfolio)
    assert any("WARNING" in v and "sustainable" in v for v in violations)


def test_trust_revocable_info() -> None:
    """Revocable trust -> INFO reminder about taxable estate."""
    portfolio = {
        "trust_config": {
            "is_trust_account": True,
            "trust_type": "revocable",
            "trust_assets_usd": 5000000,
            "estate_tax_exclusion_usd": 13610000,
            "trustee_is_beneficiary": False,
            "has_self_dealing_transaction": False,
            "annual_distribution_pct": 4,
            "generation_skipping_transfer": False,
            "gst_exemption_used_usd": 0,
        },
    }
    violations = check_trust_accounts(portfolio)
    assert any("INFO" in v and "grantor" in v for v in violations)


def test_trust_irrevocable_clean() -> None:
    """Fully compliant irrevocable trust -> no violations."""
    portfolio = {
        "trust_config": {
            "is_trust_account": True,
            "trust_type": "irrevocable",
            "trust_assets_usd": 5000000,
            "estate_tax_exclusion_usd": 13610000,
            "trustee_is_beneficiary": False,
            "has_self_dealing_transaction": False,
            "annual_distribution_pct": 4,
            "generation_skipping_transfer": False,
            "gst_exemption_used_usd": 0,
        },
    }
    assert check_trust_accounts(portfolio) == []


def test_trust_checker_registered() -> None:
    """'trust-accounts' should be in _RULE_CHECKERS."""
    assert "trust-accounts" in _RULE_CHECKERS
    assert _RULE_CHECKERS["trust-accounts"] is check_trust_accounts
