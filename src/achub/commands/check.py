"""achub check — Run rule checks against a portfolio."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from achub.commands.checkers.ai_supervision import check_ai_supervision
from achub.commands.checkers.alt_investments import check_alt_investments
from achub.commands.checkers.asset_location import check_asset_location
from achub.commands.checkers.cash_management import check_cash_management
from achub.commands.checkers.copy_trading import check_copy_trading
from achub.commands.checkers.custodial import check_custodial
from achub.commands.checkers.direct_indexing import check_direct_indexing
from achub.commands.checkers.drip import check_drip
from achub.commands.checkers.event_contracts import check_event_contracts
from achub.commands.checkers.futures import check_futures_margin
from achub.commands.checkers.gfv import check_gfv
from achub.commands.checkers.goal_allocation import check_goal_allocation
from achub.commands.checkers.income_rmd import check_income_rmd
from achub.commands.checkers.ira import check_ira_compliance
from achub.commands.checkers.margin import check_margin_maintenance
from achub.commands.checkers.margin_lending import check_margin_lending
from achub.commands.checkers.options import check_options_approval
from achub.commands.checkers.recurring import check_recurring
from achub.commands.checkers.short_selling import check_short_selling
from achub.commands.checkers.suitability import check_suitability
from achub.commands.checkers.tlh import check_tlh
from achub.commands.checkers.zero_dte import check_zero_dte

console = Console()


def _check_pdt(portfolio: dict) -> list[str]:
    """Check Pattern Day Trader rule violations.

    PDT rule: margin accounts with equity < $25,000 are limited to 3 day trades
    in a rolling 5-business-day window.
    """
    violations: list[str] = []
    account_type = portfolio.get("account_type", "").lower()
    equity = portfolio.get("equity", 0)
    day_trades_5d = portfolio.get("day_trades_count_5d", 0)

    if account_type == "margin" and equity < 25000:
        if day_trades_5d >= 4:
            violations.append(
                f"PDT VIOLATION: {day_trades_5d} day trades in 5-day window "
                f"with equity ${equity:,.2f} (< $25,000). Account may be restricted."
            )
        elif day_trades_5d >= 3:
            violations.append(
                f"PDT WARNING: {day_trades_5d} day trades in 5-day window "
                f"with equity ${equity:,.2f} (< $25,000). "
                f"Next day trade would be the 4th — potential PDT flag."
            )

    return violations


# Mapping of ETFs tracking the same index (substantially identical heuristic)
_SAME_INDEX_ETFS = {
    "SPY": "SP500", "IVV": "SP500", "VOO": "SP500",
    "QQQ": "NASDAQ100", "QQQM": "NASDAQ100",
    "IWM": "RUSSELL2000", "VTWO": "RUSSELL2000",
    "VTI": "TOTAL_US", "ITOT": "TOTAL_US", "SPTM": "TOTAL_US",
    "VXUS": "INTL_EX_US", "IXUS": "INTL_EX_US",
    "AGG": "US_AGG_BOND", "BND": "US_AGG_BOND", "SCHZ": "US_AGG_BOND",
}


def _are_substantially_identical(sym1: str, sym2: str) -> bool:
    """Check if two symbols are substantially identical for wash sale purposes."""
    if sym1 == sym2:
        return True
    # Options on same underlying (simplified: AAPL vs AAPL_C250)
    base1 = sym1.split("_")[0] if "_" in sym1 else sym1
    base2 = sym2.split("_")[0] if "_" in sym2 else sym2
    if base1 == base2:
        return True
    # Same-index ETFs
    idx1 = _SAME_INDEX_ETFS.get(sym1)
    idx2 = _SAME_INDEX_ETFS.get(sym2)
    if idx1 and idx2 and idx1 == idx2:
        return True
    return False


def _check_wash_sale(portfolio: dict) -> list[str]:
    """Check for potential wash sale violations.

    Wash sale rule: if a security is sold at a loss and the same or substantially
    identical security is purchased within 30 days before or after the sale.
    Checks across main trades, spouse trades, and other accounts.
    """
    violations: list[str] = []
    recent_trades = portfolio.get("recent_trades", [])
    positions = portfolio.get("positions", [])
    spouse_trades = portfolio.get("spouse_trades", [])
    other_account_trades = portfolio.get("other_accounts", [])

    # Combine all buy sources for cross-account checking
    all_buy_trades = list(recent_trades) + list(spouse_trades) + list(other_account_trades)

    # Collect current position symbols
    position_symbols = {p.get("symbol", "").upper() for p in positions}

    # Find loss sales
    for trade in recent_trades:
        if trade.get("action", trade.get("side", "")).lower() != "sell":
            continue
        if trade.get("pnl", trade.get("realized_pnl", 0)) >= 0:
            continue

        symbol = trade.get("symbol", "").upper()
        sell_date_str = trade.get("date", "")
        if not sell_date_str:
            continue

        try:
            sell_date = datetime.strptime(sell_date_str, "%Y-%m-%d")
        except ValueError:
            continue

        # Check if same or substantially identical symbol is still held
        for pos_sym in position_symbols:
            if _are_substantially_identical(symbol, pos_sym):
                violations.append(
                    f"WASH SALE WARNING: {symbol} sold at a loss on {sell_date_str} "
                    f"but {'same' if symbol == pos_sym else 'substantially identical'} "
                    f"security {pos_sym} still held in positions."
                )
                break
        else:
            # Check if same or substantially identical symbol was bought within 30 days
            for other_trade in all_buy_trades:
                if other_trade.get("action", other_trade.get("side", "")).lower() != "buy":
                    continue
                other_symbol = other_trade.get("symbol", "").upper()
                if not _are_substantially_identical(symbol, other_symbol):
                    continue

                buy_date_str = other_trade.get("date", "")
                if not buy_date_str:
                    continue

                try:
                    buy_date = datetime.strptime(buy_date_str, "%Y-%m-%d")
                except ValueError:
                    continue

                delta = abs((buy_date - sell_date).days)
                if delta <= 30:
                    source = ""
                    if other_trade in spouse_trades:
                        source = " (spouse account)"
                    elif other_trade in other_account_trades:
                        source = " (other account)"
                    identical = "same" if symbol == other_symbol else "substantially identical"
                    violations.append(
                        f"WASH SALE WARNING: {symbol} sold at a loss on {sell_date_str} "
                        f"and {identical} security {other_symbol} repurchased on "
                        f"{buy_date_str} ({delta} days apart, within 30-day window)"
                        f"{source}."
                    )

    return violations


# Map of rule names to checker functions
_RULE_CHECKERS = {
    "pdt": _check_pdt,
    "wash-sale": _check_wash_sale,
    "options": check_options_approval,
    "margin": check_margin_maintenance,
    "ira": check_ira_compliance,
    "futures": check_futures_margin,
    "gfv": check_gfv,
    "short-selling": check_short_selling,
    "zero-dte": check_zero_dte,
    "recurring": check_recurring,
    "tlh": check_tlh,
    "goal-allocation": check_goal_allocation,
    "asset-location": check_asset_location,
    "suitability": check_suitability,
    "drip": check_drip,
    "direct-indexing": check_direct_indexing,
    "copy-trading": check_copy_trading,
    "margin-lending": check_margin_lending,
    "income-rmd": check_income_rmd,
    "event-contracts": check_event_contracts,
    "cash-management": check_cash_management,
    "custodial": check_custodial,
    "ai-supervision": check_ai_supervision,
    "alt-investments": check_alt_investments,
}


@click.command()
@click.option("--domain", required=True, help="Domain to check rules for (e.g. trading).")
@click.option(
    "--rules", required=True,
    help="Comma-separated rules to check (e.g. pdt,wash-sale).",
)
@click.option(
    "--portfolio",
    required=True,
    type=click.Path(exists=True),
    help="Path to portfolio JSON file.",
)
@click.pass_context
def check(ctx, domain: str, rules: str, portfolio: str):
    """Run rule checks against a portfolio.

    Checks trading rules like PDT and wash-sale against your portfolio state.
    Automatically runs both Python checkers and structured YAML checks from
    content documents.

    Example: achub check --domain trading --rules pdt,wash-sale --portfolio portfolio.json
    """
    portfolio_path = Path(portfolio)
    with open(portfolio_path) as f:
        portfolio_data = json.load(f)

    rule_names = [r.strip() for r in rules.split(",")]
    all_violations: list[str] = []

    for rule_name in rule_names:
        checker = _RULE_CHECKERS.get(rule_name)
        if checker is None:
            console.print(f"[yellow]Unknown rule: {rule_name}[/yellow]")
            continue
        violations = checker(portfolio_data)
        all_violations.extend(violations)

    # Always run structured checks from content documents
    from achub.core.checker import StructuredCheckEvaluator
    from achub.core.registry import ContentRegistry

    project_root = ctx.obj["project_root"]
    registry = ContentRegistry(project_root)
    registry.build()
    evaluator = StructuredCheckEvaluator()
    items = registry.list_all(domain=domain)
    for item in items:
        checks = item.get("checks", [])
        if not checks:
            continue
        results = evaluator.evaluate_checks(checks, portfolio_data)
        for r in results:
            if not r.passed:
                all_violations.append(
                    f"[{r.severity.upper()}] {r.id}: {r.message}"
                )

    if all_violations:
        panel_lines = "\n".join(f"[red]- {v}[/red]" for v in all_violations)
        console.print(
            Panel(
                panel_lines,
                title=f"[bold red]Rule Violations ({domain})[/bold red]",
                border_style="red",
                expand=False,
            )
        )
        raise SystemExit(1)
    else:
        console.print(
            Panel(
                "[bold green]All checks passed.[/bold green]",
                title=f"Rule Check ({domain})",
                border_style="green",
                expand=False,
            )
        )
