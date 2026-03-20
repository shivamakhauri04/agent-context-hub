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
def futures_portfolio() -> dict:
    """Return a portfolio for futures margin testing.

    Futures account with /ES and /MNQ positions, $50k balance.
    """
    return {
        "account_type": "futures",
        "equity": 50000,
        "cash": 50000,
        "asset_class": "futures",
        "futures_account_balance": 50000,
        "futures_day_trade": False,
        "futures_positions": [
            {
                "symbol": "/ES",
                "contracts": 2,
                "avg_entry_price": 5200.00,
                "current_price": 5180.00,
                "unrealized_pnl": -2000.00,
            },
            {
                "symbol": "/MNQ",
                "contracts": 5,
                "avg_entry_price": 18500.00,
                "current_price": 18450.00,
                "unrealized_pnl": -500.00,
            },
        ],
        "positions": [],
        "recent_trades": [],
        "day_trades_count_5d": 0,
        "settlement_days": 1,
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


@pytest.fixture()
def gfv_portfolio() -> dict:
    """Return a portfolio for GFV testing.

    Cash account, 2 GFV in 12 months, some unsettled cash, active positions.
    """
    return {
        "account_type": "cash",
        "equity": 15000,
        "cash": 8000,
        "gfv_count_12m": 2,
        "unsettled_cash": 3000,
        "pending_buy_with_unsettled": False,
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 20,
                "avg_cost": 180.00,
                "current_price": 185.00,
                "unrealized_pnl": 100.00,
            },
        ],
        "recent_trades": [],
        "day_trades_count_5d": 0,
    }


@pytest.fixture()
def short_selling_portfolio() -> dict:
    """Return a portfolio for short selling testing.

    Margin account with short positions, locates, and margin data.
    """
    return {
        "account_type": "margin",
        "equity": 100000,
        "cash": 20000,
        "short_positions": [
            {
                "symbol": "GME",
                "quantity": 100,
                "locate_obtained": True,
                "is_hard_to_borrow": True,
                "borrow_rate_annualized": 75,
                "days_short": 5,
                "is_threshold_security": False,
            },
            {
                "symbol": "AMC",
                "quantity": 200,
                "locate_obtained": True,
                "is_hard_to_borrow": False,
                "borrow_rate_annualized": 5,
                "days_short": 3,
                "is_threshold_security": False,
            },
        ],
        "short_margin_equity": 45000,
        "short_market_value": 100000,
        "threshold_securities": ["BBBY"],
        "positions": [],
        "recent_trades": [],
        "day_trades_count_5d": 0,
    }


@pytest.fixture()
def zero_dte_portfolio() -> dict:
    """Return a portfolio for 0DTE options testing.

    Margin account with 0DTE positions, options approval level 3.
    """
    return {
        "account_type": "margin",
        "equity": 100000,
        "cash": 30000,
        "options_approval_level": 3,
        "zero_dte_positions": [
            {
                "symbol": "SPX_P5200",
                "direction": "short",
                "max_loss": 2000,
                "exercise_cost": 52000,
                "contracts": 1,
            },
            {
                "symbol": "SPX_C5250",
                "direction": "long",
                "max_loss": 1500,
                "exercise_cost": 0,
                "contracts": 2,
            },
        ],
        "zero_dte_max_portfolio_pct": 0.05,
        "positions": [],
        "recent_trades": [],
        "day_trades_count_5d": 0,
    }


@pytest.fixture()
def recurring_portfolio() -> dict:
    """Return a portfolio for recurring investments testing.

    Cash account with recurring investment schedule.
    """
    return {
        "account_type": "cash",
        "equity": 50000,
        "cash": 5000,
        "recurring_investments": [
            {"symbol": "VOO", "amount_usd": 500, "frequency": "monthly"},
            {"symbol": "VTI", "amount_usd": 100, "frequency": "weekly"},
        ],
        "recurring_total_monthly_usd": 933,
        "positions": [],
        "recent_trades": [],
        "day_trades_count_5d": 0,
    }


@pytest.fixture()
def tlh_portfolio() -> dict:
    """Return a portfolio for tax-loss harvesting testing.

    Margin account with harvest opportunities, IRA cross-account risk,
    and DRIP enabled on a harvest candidate.
    """
    return {
        "account_type": "margin",
        "equity": 100000,
        "cash": 20000,
        "day_trades_count_5d": 0,
        "positions": [
            {
                "symbol": "VOO",
                "quantity": 100,
                "avg_cost": 450.00,
                "current_price": 420.00,
                "unrealized_pnl": -3000.00,
            },
        ],
        "recent_trades": [],
        "harvest_opportunities": [
            {
                "symbol": "VOO",
                "unrealized_loss": 3000,
                "holding_days": 200,
                "proposed_replacement": "IVV",
            },
            {
                "symbol": "AAPL",
                "unrealized_loss": 1000,
                "holding_days": 90,
                "proposed_replacement": "MSFT",
            },
        ],
        "capital_gains_ytd": 2000,
        "capital_losses_ytd": 8000,
        "loss_carryforward": 0,
        "ira_recent_purchases": [{"symbol": "AAPL", "date": "2026-03-10"}],
        "drip_enabled_symbols": ["VOO"],
    }


@pytest.fixture()
def goal_portfolio() -> dict:
    """Return a portfolio for goal-based allocation testing.

    Short-horizon house down payment goal with high equity allocation.
    """
    return {
        "account_type": "cash",
        "equity": 50000,
        "cash": 10000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "goal_type": "house_down_payment",
        "goal_time_horizon_years": 2,
        "goal_target_amount": 60000,
        "customer_risk_score": 3,
        "goal_equity_pct": 50,
        "goal_bond_pct": 30,
        "goal_cash_pct": 20,
    }


@pytest.fixture()
def asset_location_portfolio() -> dict:
    """Return a portfolio for asset location testing.

    Household with bonds/REITs in taxable and munis in IRA.
    """
    return {
        "account_type": "margin",
        "equity": 500000,
        "cash": 50000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "household_accounts": [
            {
                "account_id": "taxable-1",
                "account_tax_type": "taxable",
                "holdings": [
                    {
                        "symbol": "BND",
                        "asset_category": "us_aggregate_bond",
                        "allocation_pct": 35,
                    },
                    {
                        "symbol": "VNQ",
                        "asset_category": "reit",
                        "allocation_pct": 15,
                    },
                    {
                        "symbol": "VTI",
                        "asset_category": "us_equity_index",
                        "allocation_pct": 50,
                    },
                ],
            },
            {
                "account_id": "ira-1",
                "account_tax_type": "traditional_ira",
                "holdings": [
                    {
                        "symbol": "MUB",
                        "asset_category": "municipal_bond",
                        "allocation_pct": 40,
                    },
                    {
                        "symbol": "VTI",
                        "asset_category": "us_equity_index",
                        "allocation_pct": 60,
                    },
                ],
            },
        ],
    }


@pytest.fixture()
def suitability_portfolio() -> dict:
    """Return a portfolio for suitability testing.

    Conservative customer with aggressive pending strategy and high turnover.
    """
    return {
        "account_type": "margin",
        "equity": 50000,
        "cash": 10000,
        "day_trades_count_5d": 0,
        "positions": [
            {
                "symbol": "TSLA",
                "quantity": 200,
                "avg_cost": 170.00,
                "current_price": 175.00,
                "unrealized_pnl": 1000.00,
            },
        ],
        "recent_trades": [],
        "customer_risk_tolerance": 2,
        "customer_experience_level": 2,
        "pending_strategies": [
            {
                "strategy": "naked_put",
                "symbol": "TSLA",
                "risk_level": 5,
                "complexity": 4,
            },
        ],
        "turnover_ratio_annual": 8.5,
        "cost_equity_ratio_annual": 0.25,
    }


@pytest.fixture()
def direct_indexing_portfolio() -> dict:
    """Return a portfolio for direct indexing testing.

    $250K account with individual S&P 500 positions, VOO ETF overlap,
    and elevated tracking error.
    """
    return {
        "account_type": "margin",
        "equity": 250000,
        "cash": 30000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "direct_index_config": {
            "benchmark_index": "SP500",
            "minimum_account_size": 100000,
            "individual_positions": [
                {"symbol": "AAPL", "weight_pct": 6.5, "unrealized_pnl": -1200},
                {"symbol": "MSFT", "weight_pct": 5.8, "unrealized_pnl": 800},
                {"symbol": "GOOGL", "weight_pct": 3.2, "unrealized_pnl": -450},
            ],
            "tracking_error_pct": 2.5,
            "etf_holdings": ["VOO"],
        },
    }


@pytest.fixture()
def copy_trading_portfolio() -> dict:
    """Return a portfolio for copy trading testing.

    Conservative investor copying an aggressive leader with margin/options.
    """
    return {
        "account_type": "margin",
        "equity": 10000,
        "cash": 3000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "customer_risk_tolerance": 2,
        "copy_trading_config": {
            "leader_username": "aggressive_options_trader",
            "leader_risk_level": 8,
            "copy_allocation_usd": 5000,
            "leader_portfolio_size": 1000000,
            "leader_uses_margin": True,
            "leader_uses_options": True,
        },
    }


@pytest.fixture()
def margin_lending_portfolio() -> dict:
    """Return a portfolio for margin lending testing.

    $500K portfolio with $340K loan near maintenance threshold,
    concentrated collateral.
    """
    return {
        "account_type": "margin",
        "equity": 500000,
        "cash": 50000,
        "day_trades_count_5d": 0,
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 500,
                "avg_cost": 180.00,
                "current_price": 195.00,
                "unrealized_pnl": 7500,
            },
        ],
        "recent_trades": [],
        "margin_loan": {
            "loan_balance": 340000,
            "collateral_value": 500000,
            "maintenance_ltv_pct": 70,
            "interest_rate_annual": 6.5,
            "loan_purpose": "general",
            "largest_collateral_position_pct": 55,
        },
    }


@pytest.fixture()
def income_rmd_portfolio() -> dict:
    """Return a portfolio for income/RMD testing.

    Age 75, traditional IRA, RMD required, under-scheduled distribution,
    high equity allocation.
    """
    return {
        "account_type": "cash",
        "equity": 500000,
        "cash": 40000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "account_holder_age": 75,
        "rmd_config": {
            "rmd_required": True,
            "prior_year_end_balance": 500000,
            "rmd_amount_scheduled": 15000,
            "rmd_amount_taken_ytd": 0,
            "withdrawal_rate_pct": 3.5,
            "income_equity_pct": 70,
        },
    }


@pytest.fixture()
def event_contracts_portfolio() -> dict:
    """Return a portfolio for event contracts / prediction markets testing.

    Two positions: economics and finance categories, within limits.
    """
    return {
        "account_type": "cash",
        "equity": 50000,
        "cash": 10000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "event_contract_config": {
            "positions": [
                {
                    "event_id": "fed-rate-march-2026",
                    "direction": "yes",
                    "contracts": 2000,
                    "price_per_contract": 0.35,
                    "event_category": "economics",
                },
                {
                    "event_id": "sp500-above-5500",
                    "direction": "no",
                    "contracts": 3000,
                    "price_per_contract": 0.55,
                    "event_category": "finance",
                },
            ],
            "platform_position_limit_usd": 50000,
            "total_exposure_usd": 2350,
            "collateral_available": 10000,
        },
    }


@pytest.fixture()
def cash_management_portfolio() -> dict:
    """Return a portfolio for cash management / sweep testing.

    Bank deposit sweep across 3 banks, external deposit overlap at Bank A.
    """
    return {
        "account_type": "cash",
        "equity": 500000,
        "cash": 35000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "cash_management_config": {
            "sweep_type": "bank_deposit",
            "sweep_banks": [
                {"bank_name": "Partner Bank A", "deposit_amount": 200000},
                {"bank_name": "Partner Bank B", "deposit_amount": 150000},
                {"bank_name": "Partner Bank C", "deposit_amount": 100000},
            ],
            "external_deposits_same_banks": [
                {"bank_name": "Partner Bank A", "amount": 80000},
            ],
            "idle_cash_exempt": False,
        },
    }


@pytest.fixture()
def custodial_portfolio() -> dict:
    """Return a portfolio for custodial account (UTMA/UGMA) testing.

    14-year-old minor, state majority at 18, moderate unearned income.
    """
    return {
        "account_type": "cash",
        "equity": 25000,
        "cash": 3000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "custodial_config": {
            "is_custodial": True,
            "minor_age": 14,
            "state_age_of_majority": 18,
            "unearned_income_ytd": 1800,
            "has_options": False,
            "has_margin": False,
            "has_futures": False,
            "has_short_positions": False,
        },
    }


@pytest.fixture()
def ai_supervision_portfolio() -> dict:
    """Return a portfolio for AI supervision compliance testing.

    AI-generated content, fully compliant configuration.
    """
    return {
        "account_type": "margin",
        "equity": 100000,
        "cash": 20000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
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


@pytest.fixture()
def alt_investments_portfolio() -> dict:
    """Return a portfolio for alternative investments testing.

    Accredited investor with liquid alt ETFs, within concentration cap.
    """
    return {
        "account_type": "margin",
        "equity": 200000,
        "cash": 15000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "customer_experience_level": 4,
        "alt_investment_config": {
            "is_accredited_investor": True,
            "alt_positions": [
                {
                    "symbol": "QAI",
                    "value_usd": 15000,
                    "expense_ratio_pct": 0.75,
                    "is_liquid_alt_etf": True,
                    "has_lockup": False,
                    "lockup_days_remaining": 0,
                },
                {
                    "symbol": "BTAL",
                    "value_usd": 10000,
                    "expense_ratio_pct": 0.55,
                    "is_liquid_alt_etf": True,
                    "has_lockup": False,
                    "lockup_days_remaining": 0,
                },
            ],
            "alt_allocation_cap_pct": 20,
        },
    }


@pytest.fixture()
def crypto_portfolio() -> dict:
    """Return a portfolio for crypto compliance testing.

    BTC/ETH/SOL positions, ETH staking with rewards, over-concentrated.
    """
    return {
        "account_type": "margin",
        "equity": 100000,
        "cash": 15000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "crypto_config": {
            "crypto_positions": [
                {
                    "symbol": "BTC",
                    "quantity": 0.5,
                    "value_usd": 30000,
                    "is_staking": False,
                    "staking_rewards_ytd_usd": 0,
                },
                {
                    "symbol": "ETH",
                    "quantity": 10,
                    "value_usd": 25000,
                    "is_staking": True,
                    "staking_rewards_ytd_usd": 850,
                },
            ],
            "crypto_allocation_pct": 55,
            "crypto_allocation_cap_pct": 20,
            "sipc_awareness_disclosed": True,
            "wash_sale_tracking_enabled": True,
            "recent_crypto_sales_at_loss": [],
        },
    }


@pytest.fixture()
def drift_portfolio() -> dict:
    """Return a portfolio for portfolio drift monitoring testing.

    Target allocations with significant drift in equities and bonds.
    """
    return {
        "account_type": "margin",
        "equity": 200000,
        "cash": 20000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "target_allocations": [
            {"asset_class": "us_equity", "target_pct": 60, "current_pct": 75},
            {"asset_class": "bonds", "target_pct": 30, "current_pct": 18},
            {"asset_class": "cash", "target_pct": 10, "current_pct": 7},
        ],
        "rebalance_threshold_pct": 5,
        "last_rebalance_date": "2025-06-15",
    }


@pytest.fixture()
def esg_portfolio() -> dict:
    """Return a portfolio for ESG screening testing.

    ESG enabled, provider disclosed, one position with excluded sectors.
    """
    return {
        "account_type": "margin",
        "equity": 150000,
        "cash": 10000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
        "esg_config": {
            "esg_enabled": True,
            "provider_disclosed": True,
            "esg_positions": [
                {
                    "symbol": "ESGU",
                    "esg_score": 82,
                    "esg_label": "ESG Leader",
                    "holds_excluded_sectors": False,
                },
                {
                    "symbol": "XLE",
                    "esg_score": 30,
                    "esg_label": "Energy Transition",
                    "holds_excluded_sectors": True,
                },
            ],
            "exclusion_categories": ["tobacco", "thermal_coal"],
            "tracking_error_pct": 1.5,
            "tracking_error_cap_pct": 2.0,
            "is_erisa_account": False,
        },
    }


@pytest.fixture()
def adversarial_ai_portfolio() -> dict:
    """Return a portfolio for adversarial AI testing.

    Fully compliant adversarial AI configuration.
    """
    return {
        "account_type": "margin",
        "equity": 100000,
        "cash": 20000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
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


@pytest.fixture()
def trust_portfolio() -> dict:
    """Return a portfolio for trust account testing.

    Irrevocable trust, $5M assets, within estate tax exclusion.
    """
    return {
        "account_type": "cash",
        "equity": 5000000,
        "cash": 200000,
        "day_trades_count_5d": 0,
        "positions": [],
        "recent_trades": [],
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
