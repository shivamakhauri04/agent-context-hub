"""Tax-loss harvesting checker."""
from __future__ import annotations

from datetime import datetime

_SAME_INDEX_ETFS = {
    "SPY": "SP500", "IVV": "SP500", "VOO": "SP500",
    "QQQ": "NASDAQ100", "QQQM": "NASDAQ100",
    "IWM": "RUSSELL2000", "VTWO": "RUSSELL2000",
    "VTI": "TOTAL_US", "ITOT": "TOTAL_US", "SPTM": "TOTAL_US",
    "VXUS": "INTL_EX_US", "IXUS": "INTL_EX_US",
    "AGG": "US_AGG_BOND", "BND": "US_AGG_BOND", "SCHZ": "US_AGG_BOND",
}


def check_tlh(portfolio: dict) -> list[str]:
    """Check tax-loss harvesting opportunities for issues.

    Skips if no ``harvest_opportunities``.  Flags:
    - CRITICAL if replacement tracks same index (wash sale risk)
    - WARNING if net capital losses exceed $3,000 annual deduction limit
    - CRITICAL if cross-account IRA wash sale detected
    - INFO if short-term losses should be prioritized over long-term
    """
    violations: list[str] = []
    opportunities = portfolio.get("harvest_opportunities", [])

    if not opportunities:
        return violations

    _check_substantially_identical(opportunities, violations)
    _check_annual_cap(portfolio, violations)
    _check_ira_cross_account(portfolio, opportunities, violations)
    _check_short_term_priority(opportunities, violations)

    return violations


def _check_substantially_identical(
    opportunities: list[dict], violations: list[str]
) -> None:
    for opp in opportunities:
        symbol = opp.get("symbol", "").upper()
        replacement = opp.get("proposed_replacement", "").upper()
        if not symbol or not replacement:
            continue
        idx_sym = _SAME_INDEX_ETFS.get(symbol)
        idx_rep = _SAME_INDEX_ETFS.get(replacement)
        if idx_sym and idx_rep and idx_sym == idx_rep:
            violations.append(
                f"TLH CRITICAL: Proposed replacement {replacement} for "
                f"{symbol} tracks the same index ({idx_sym}) -- "
                f"substantially identical, wash sale risk."
            )


def _check_annual_cap(portfolio: dict, violations: list[str]) -> None:
    losses = portfolio.get("capital_losses_ytd", 0)
    gains = portfolio.get("capital_gains_ytd", 0)
    net = losses - gains
    if net > 3000 and not portfolio.get("loss_carryforward"):
        violations.append(
            f"TLH WARNING: Net capital losses ${net:,.0f} exceed "
            f"$3,000 annual deduction limit. Excess must be carried forward."
        )


def _check_ira_cross_account(
    portfolio: dict, opportunities: list[dict], violations: list[str]
) -> None:
    harvest_symbols = {o.get("symbol", "").upper() for o in opportunities}
    now = datetime.now()
    for purchase in portfolio.get("ira_recent_purchases", []):
        sym = purchase.get("symbol", "").upper()
        if sym not in harvest_symbols:
            continue
        date_str = purchase.get("date", "")
        if not date_str:
            continue
        try:
            pdate = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        if abs((now - pdate).days) <= 30:
            violations.append(
                f"TLH CRITICAL: {sym} in harvest list was purchased in "
                f"IRA on {date_str} -- cross-account wash sale, loss "
                f"PERMANENTLY disallowed."
            )


def _check_short_term_priority(
    opportunities: list[dict], violations: list[str]
) -> None:
    short_term = [
        o for o in opportunities if o.get("holding_days", 0) <= 365
    ]
    for opp in opportunities:
        if opp.get("holding_days", 0) <= 365:
            continue
        symbol = opp.get("symbol", "")
        loss = abs(opp.get("unrealized_loss", 0))
        for st in short_term:
            st_loss = abs(st.get("unrealized_loss", 0))
            if st_loss >= loss:
                violations.append(
                    f"TLH INFO: Consider harvesting short-term loss "
                    f"{st.get('symbol', '')} (${st_loss:,.0f}, "
                    f"{st.get('holding_days', 0)}d) before long-term "
                    f"loss {symbol} -- higher tax value."
                )
                break
