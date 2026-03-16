"""achub check — Run rule checks against a portfolio."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

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


def _check_wash_sale(portfolio: dict) -> list[str]:
    """Check for potential wash sale violations.

    Wash sale rule: if a security is sold at a loss and the same or substantially
    identical security is purchased within 30 days before or after the sale.
    """
    violations: list[str] = []
    recent_trades = portfolio.get("recent_trades", [])
    positions = portfolio.get("positions", [])

    # Collect current position symbols
    position_symbols = {p.get("symbol", "").upper() for p in positions}

    # Find loss sales
    for trade in recent_trades:
        if trade.get("side", "").lower() != "sell":
            continue
        if trade.get("realized_pnl", 0) >= 0:
            continue

        symbol = trade.get("symbol", "").upper()
        sell_date_str = trade.get("date", "")
        if not sell_date_str:
            continue

        try:
            sell_date = datetime.strptime(sell_date_str, "%Y-%m-%d")
        except ValueError:
            continue

        # Check if same symbol is still held in positions
        if symbol in position_symbols:
            violations.append(
                f"WASH SALE WARNING: {symbol} sold at a loss on {sell_date_str} "
                f"but still held in positions."
            )
            continue

        # Check if same symbol was bought within 30 days
        for other_trade in recent_trades:
            if other_trade.get("side", "").lower() != "buy":
                continue
            if other_trade.get("symbol", "").upper() != symbol:
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
                violations.append(
                    f"WASH SALE WARNING: {symbol} sold at a loss on {sell_date_str} "
                    f"and repurchased on {buy_date_str} ({delta} days apart, within 30-day window)."
                )

    return violations


# Map of rule names to checker functions
_RULE_CHECKERS = {
    "pdt": _check_pdt,
    "wash-sale": _check_wash_sale,
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
