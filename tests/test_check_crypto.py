"""Tests for crypto compliance checker."""
from __future__ import annotations

from achub.commands.check import _RULE_CHECKERS
from achub.commands.checkers.crypto import check_crypto


def test_crypto_no_config_skips() -> None:
    """No crypto_config -> skip."""
    portfolio = {"account_type": "margin", "equity": 50000}
    assert check_crypto(portfolio) == []


def test_crypto_no_sipc_disclosure_critical() -> None:
    """Positions without SIPC awareness -> CRITICAL."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [
                {"symbol": "BTC", "quantity": 1, "value_usd": 60000,
                 "is_staking": False, "staking_rewards_ytd_usd": 0},
            ],
            "sipc_awareness_disclosed": False,
            "wash_sale_tracking_enabled": True,
            "crypto_allocation_pct": 10,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [],
        },
    }
    violations = check_crypto(portfolio)
    assert any("CRITICAL" in v and "SIPC" in v for v in violations)


def test_crypto_wash_sale_critical() -> None:
    """Crypto sold at loss and repurchased within 30 days -> CRITICAL."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [],
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": True,
            "crypto_allocation_pct": 5,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [
                {"symbol": "ETH", "date": "2026-03-01",
                 "loss_usd": 1500, "repurchased_within_30d": True},
            ],
        },
    }
    violations = check_crypto(portfolio)
    assert any("CRITICAL" in v and "wash sale" in v for v in violations)


def test_crypto_over_concentration_warning() -> None:
    """Crypto allocation exceeds cap -> WARNING."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [],
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": True,
            "crypto_allocation_pct": 35,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [],
        },
    }
    violations = check_crypto(portfolio)
    assert any("WARNING" in v and "over-concentrated" in v for v in violations)


def test_crypto_staking_tax_warning() -> None:
    """Staking rewards > $600 YTD -> WARNING."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [
                {"symbol": "SOL", "quantity": 100, "value_usd": 15000,
                 "is_staking": True, "staking_rewards_ytd_usd": 850},
            ],
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": True,
            "crypto_allocation_pct": 10,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [],
        },
    }
    violations = check_crypto(portfolio)
    assert any("WARNING" in v and "1099-MISC" in v for v in violations)


def test_crypto_staking_under_600_no_warning() -> None:
    """Staking rewards <= $600 -> no tax warning."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [
                {"symbol": "ETH", "quantity": 5, "value_usd": 10000,
                 "is_staking": True, "staking_rewards_ytd_usd": 400},
            ],
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": True,
            "crypto_allocation_pct": 10,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [],
        },
    }
    violations = check_crypto(portfolio)
    assert not any("1099-MISC" in v for v in violations)


def test_crypto_wash_sale_tracking_disabled_warning() -> None:
    """Wash sale tracking disabled -> WARNING."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [],
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": False,
            "crypto_allocation_pct": 5,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [],
        },
    }
    violations = check_crypto(portfolio)
    assert any("WARNING" in v and "Wash sale tracking" in v for v in violations)


def test_crypto_all_clean() -> None:
    """Fully compliant crypto config -> no violations."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [
                {"symbol": "BTC", "quantity": 0.5, "value_usd": 30000,
                 "is_staking": False, "staking_rewards_ytd_usd": 0},
            ],
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": True,
            "crypto_allocation_pct": 10,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [],
        },
    }
    assert check_crypto(portfolio) == []


def test_crypto_wash_sale_no_repurchase_clean() -> None:
    """Crypto sold at loss but NOT repurchased -> no wash sale violation."""
    portfolio = {
        "crypto_config": {
            "crypto_positions": [],
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": True,
            "crypto_allocation_pct": 5,
            "crypto_allocation_cap_pct": 20,
            "recent_crypto_sales_at_loss": [
                {"symbol": "ETH", "date": "2026-02-01",
                 "loss_usd": 2000, "repurchased_within_30d": False},
            ],
        },
    }
    violations = check_crypto(portfolio)
    assert not any("wash sale" in v for v in violations)


def test_crypto_checker_registered() -> None:
    """'crypto' should be in _RULE_CHECKERS."""
    assert "crypto" in _RULE_CHECKERS
    assert _RULE_CHECKERS["crypto"] is check_crypto
