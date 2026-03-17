"""Tests for MCP server tool handler functions."""
from __future__ import annotations

import pytest

from achub.integrations.mcp import _build_registry
from achub.utils.paths import find_project_root


@pytest.fixture
def registry():
    return _build_registry()


def test_find_project_root():
    root = find_project_root()
    assert (root / "pyproject.toml").exists()


def test_registry_search(registry):
    results = registry.search("wash sale")
    assert len(results) > 0
    assert any("wash" in r.get("content_id", "").lower() for r in results)


def test_registry_get(registry):
    content = registry.get("trading/regulations/pdt-rule/rules")
    assert content is not None
    assert content["metadata"]["title"] == "Pattern Day Trader (PDT) Rule"


def test_registry_list(registry):
    items = registry.list_all(domain="trading")
    assert len(items) >= 8


def test_registry_list_with_category(registry):
    items = registry.list_all(domain="trading", category="regulations")
    assert len(items) >= 2


def test_check_pdt_via_checker():
    from achub.commands.check import _check_pdt

    violations = _check_pdt({
        "account_type": "margin",
        "equity": 15000,
        "day_trades_count_5d": 4,
    })
    assert len(violations) == 1
    assert "PDT VIOLATION" in violations[0]


def test_check_wash_sale_via_checker():
    from achub.commands.check import _check_wash_sale

    violations = _check_wash_sale({
        "recent_trades": [
            {"symbol": "TSLA", "action": "sell", "quantity": 10, "price": 165.0,
             "date": "2026-03-01", "pnl": -2500.0},
            {"symbol": "TSLA", "action": "buy", "quantity": 10, "price": 170.0,
             "date": "2026-03-16", "pnl": 0},
        ],
        "positions": [],
    })
    assert len(violations) >= 1
    assert any("WASH SALE" in v for v in violations)
