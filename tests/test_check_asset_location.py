"""Tests for asset location (tax-efficiency) checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.asset_location import check_asset_location


def test_location_bonds_in_taxable_warning() -> None:
    """Taxable account has 30% bonds while traditional IRA exists -> WARNING."""
    portfolio = {
        "household_accounts": [
            {
                "account_id": "taxable-1",
                "account_tax_type": "taxable",
                "holdings": [
                    {"symbol": "BND", "asset_category": "us_aggregate_bond", "allocation_pct": 30},
                    {"symbol": "VTI", "asset_category": "us_equity_index", "allocation_pct": 70},
                ],
            },
            {
                "account_id": "ira-1",
                "account_tax_type": "traditional_ira",
                "holdings": [
                    {"symbol": "VTI", "asset_category": "us_equity_index", "allocation_pct": 100},
                ],
            },
        ],
    }
    violations = check_asset_location(portfolio)
    assert any("WARNING" in v and "bond" in v.lower() for v in violations)


def test_location_reits_in_taxable_warning() -> None:
    """Taxable account holds REITs while IRA exists -> WARNING."""
    portfolio = {
        "household_accounts": [
            {
                "account_id": "taxable-1",
                "account_tax_type": "taxable",
                "holdings": [
                    {"symbol": "VNQ", "asset_category": "reit", "allocation_pct": 20},
                    {"symbol": "VTI", "asset_category": "us_equity_index", "allocation_pct": 80},
                ],
            },
            {
                "account_id": "ira-1",
                "account_tax_type": "traditional_ira",
                "holdings": [
                    {"symbol": "VTI", "asset_category": "us_equity_index", "allocation_pct": 100},
                ],
            },
        ],
    }
    violations = check_asset_location(portfolio)
    assert any("WARNING" in v and "reit" in v.lower() for v in violations)


def test_location_municipal_bonds_in_ira_warning() -> None:
    """Traditional IRA holds municipal bonds -> WARNING (tax-exempt wasted)."""
    portfolio = {
        "household_accounts": [
            {
                "account_id": "ira-1",
                "account_tax_type": "traditional_ira",
                "holdings": [
                    {"symbol": "MUB", "asset_category": "municipal_bond", "allocation_pct": 40},
                    {"symbol": "VTI", "asset_category": "us_equity_index", "allocation_pct": 60},
                ],
            },
        ],
    }
    violations = check_asset_location(portfolio)
    assert any("WARNING" in v and "municipal" in v.lower() for v in violations)


def test_location_optimal_placement_passes() -> None:
    """Bonds in IRA, equities in taxable -> no violations."""
    portfolio = {
        "household_accounts": [
            {
                "account_id": "taxable-1",
                "account_tax_type": "taxable",
                "holdings": [
                    {"symbol": "VTI", "asset_category": "us_equity_index", "allocation_pct": 100},
                ],
            },
            {
                "account_id": "ira-1",
                "account_tax_type": "traditional_ira",
                "holdings": [
                    {"symbol": "BND", "asset_category": "us_aggregate_bond", "allocation_pct": 100},
                ],
            },
        ],
    }
    violations = check_asset_location(portfolio)
    assert violations == []


def test_location_no_household_accounts_skips() -> None:
    """No household_accounts -> empty list."""
    portfolio = {
        "equity": 50000,
        "cash": 10000,
    }
    violations = check_asset_location(portfolio)
    assert violations == []


def test_location_checker_registered() -> None:
    """'asset-location' should be in _RULE_CHECKERS."""
    assert "asset-location" in _RULE_CHECKERS
    assert _RULE_CHECKERS["asset-location"] is check_asset_location
