"""Direct indexing checker."""
from __future__ import annotations

_BENCHMARK_ETFS = {
    "SPY": "SP500", "IVV": "SP500", "VOO": "SP500",
    "QQQ": "NASDAQ100", "QQQM": "NASDAQ100",
    "IWM": "RUSSELL2000", "VTWO": "RUSSELL2000",
    "VTI": "TOTAL_US", "ITOT": "TOTAL_US", "SPTM": "TOTAL_US",
    "VXUS": "INTL_EX_US", "IXUS": "INTL_EX_US",
}


def check_direct_indexing(portfolio: dict) -> list[str]:
    """Check direct indexing portfolio for issues.

    Skips if no ``direct_index_config``.  Flags:
    - CRITICAL if equity below minimum account size
    - CRITICAL if individual stock sold at loss overlaps with held ETF benchmark
    - WARNING if tracking error exceeds 2%
    """
    violations: list[str] = []
    config = portfolio.get("direct_index_config")

    if not config:
        return violations

    _check_minimum_account_size(portfolio, config, violations)
    _check_etf_wash_sale_overlap(config, violations)
    _check_tracking_error(config, violations)

    return violations


def _check_minimum_account_size(
    portfolio: dict, config: dict, violations: list[str]
) -> None:
    equity = portfolio.get("equity", 0)
    minimum = config.get("minimum_account_size", 100000)
    if equity < minimum:
        violations.append(
            f"DIRECT INDEXING CRITICAL: Account equity ${equity:,.0f} is "
            f"below minimum ${minimum:,.0f} for direct indexing. "
            f"Transaction costs will overwhelm TLH benefits."
        )


def _check_etf_wash_sale_overlap(
    config: dict, violations: list[str]
) -> None:
    individual = config.get("individual_positions", [])
    etf_holdings = {e.upper() for e in config.get("etf_holdings", [])}
    benchmark = config.get("benchmark_index", "").upper()

    if not etf_holdings or not individual:
        return

    etf_benchmarks = {_BENCHMARK_ETFS.get(e) for e in etf_holdings} - {None}

    for pos in individual:
        pnl = pos.get("unrealized_pnl", 0)
        if pnl >= 0:
            continue
        symbol = pos.get("symbol", "").upper()
        if benchmark and benchmark in etf_benchmarks:
            violations.append(
                f"DIRECT INDEXING CRITICAL: {symbol} has unrealized loss "
                f"but portfolio holds ETF(s) tracking {benchmark} -- "
                f"selling {symbol} at a loss is a wash sale risk."
            )


def _check_tracking_error(
    config: dict, violations: list[str]
) -> None:
    tracking_error = config.get("tracking_error_pct", 0)
    if tracking_error > 2.0:
        violations.append(
            f"DIRECT INDEXING WARNING: Tracking error {tracking_error:.1f}% "
            f"exceeds 2.0% threshold. Portfolio no longer meaningfully "
            f"replicates the benchmark index."
        )
