from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def project_root() -> Path:
    """Return the path to the agent-context-hub project root."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture()
def domains_dir(project_root: Path) -> Path:
    """Return the path to the domains directory."""
    return project_root / "domains"


@pytest.fixture()
def schemas_dir(project_root: Path) -> Path:
    """Return the path to the schemas directory."""
    return project_root / "schemas"


@pytest.fixture()
def sample_content_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with a sample domain structure.

    Layout::
        tmp_path/
            domains/
                test-domain/
                    DOMAIN.md
                    category/
                        topic/
                            rules.md
    """
    domain_dir = tmp_path / "domains" / "test-domain"
    domain_dir.mkdir(parents=True)

    domain_md = domain_dir / "DOMAIN.md"
    domain_md.write_text(
        "---\n"
        "name: test-domain\n"
        "description: A test domain for unit tests\n"
        "---\n\n"
        "# Test Domain\n\nThis is a test domain.\n"
    )

    topic_dir = domain_dir / "category" / "topic"
    topic_dir.mkdir(parents=True)

    rules_md = topic_dir / "rules.md"
    rules_md.write_text(
        "---\n"
        'id: "test-domain/category/topic/rules"\n'
        'title: "Test Topic Rules"\n'
        'domain: "test-domain"\n'
        'version: "1.0.0"\n'
        'category: "category"\n'
        "tags:\n"
        "  - testing\n"
        "  - sample\n"
        'severity: "medium"\n'
        'last_verified: "2026-03-01"\n'
        "---\n\n"
        "# Test Topic Rules\n\n"
        "## Rules\n\n"
        "1. This is rule one.\n"
        "2. This is rule two.\n"
    )

    return tmp_path


@pytest.fixture()
def sample_portfolio() -> dict:
    """Return a sample portfolio dict matching the portfolio-state schema.

    Margin account, $20k equity, 3 day trades, some positions, and a TSLA
    loss sale 15 days ago.
    """
    return {
        "account_type": "margin",
        "equity": 20000,
        "cash": 5000,
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 50,
                "avg_cost": 178.50,
                "current_price": 185.20,
                "unrealized_pnl": 335.0,
            },
            {
                "symbol": "MSFT",
                "quantity": 25,
                "avg_cost": 415.00,
                "current_price": 420.50,
                "unrealized_pnl": 137.50,
            },
        ],
        "recent_trades": [
            {
                "symbol": "TSLA",
                "side": "sell",
                "quantity": 10,
                "price": 165.00,
                "date": "2026-03-01",
                "realized_pnl": -2500.00,
            },
            {
                "symbol": "NVDA",
                "side": "buy",
                "quantity": 5,
                "price": 890.00,
                "date": "2026-03-10",
                "realized_pnl": 0,
            },
            {
                "symbol": "NVDA",
                "side": "sell",
                "quantity": 5,
                "price": 895.00,
                "date": "2026-03-10",
                "realized_pnl": 25.00,
            },
            {
                "symbol": "SPY",
                "side": "buy",
                "quantity": 20,
                "price": 520.00,
                "date": "2026-03-12",
                "realized_pnl": 0,
            },
            {
                "symbol": "SPY",
                "side": "sell",
                "quantity": 20,
                "price": 522.00,
                "date": "2026-03-12",
                "realized_pnl": 40.00,
            },
        ],
        "day_trades_count_5d": 3,
    }


@pytest.fixture()
def options_portfolio() -> dict:
    """Return a portfolio for options approval testing.

    Margin account, level 2 approval, pending strategies, expiring options.
    """
    return {
        "account_type": "margin",
        "equity": 50000,
        "cash": 10000,
        "options_approval_level": 2,
        "pending_options_strategies": [
            {"strategy": "long_call", "symbol": "AAPL"},
            {"strategy": "naked_call", "symbol": "TSLA"},
        ],
        "expiring_options": [
            {"symbol": "AAPL_C200", "exercise_cost": 20000},
            {"symbol": "MSFT_C400", "exercise_cost": 5000},
        ],
        "positions": [],
        "recent_trades": [],
    }


@pytest.fixture()
def ira_portfolio() -> dict:
    """Return a portfolio for IRA compliance testing.

    Roth IRA, age 35, $5k contributed, $120k MAGI, single filer.
    """
    return {
        "ira_type": "roth",
        "ira_contribution_ytd": 5000,
        "account_holder_age": 35,
        "magi": 120000,
        "filing_status": "single",
        "withdrawal_amount": 0,
    }


@pytest.fixture()
def margin_portfolio() -> dict:
    """Return a portfolio for margin maintenance testing.

    Margin account with equity/market_value set for ratio testing.
    """
    return {
        "account_type": "margin",
        "equity": 30000,
        "market_value": 100000,
        "cash": 5000,
        "house_margin_requirement": 0.30,
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 200,
                "avg_cost": 178.50,
                "current_price": 185.00,
            },
            {
                "symbol": "MSFT",
                "quantity": 100,
                "avg_cost": 415.00,
                "current_price": 420.00,
            },
        ],
        "recent_trades": [],
    }
