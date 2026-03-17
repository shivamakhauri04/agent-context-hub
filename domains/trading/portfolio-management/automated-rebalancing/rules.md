---
id: "trading/portfolio-management/automated-rebalancing/rules"
title: "Automated Portfolio Rebalancing"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - rebalancing
  - drift-threshold
  - tax-aware
  - asset-location
  - tolerance-bands
  - wash-sale
severity: "HIGH"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - robo-advisors
related:
  - "trading/regulations/wash-sale/rules"
  - "trading/regulations/tax-loss-harvesting/rules"
  - "trading/market-structure/t1-settlement/reference"
---

# Automated Portfolio Rebalancing

## Summary

Automated portfolio rebalancing adjusts portfolio holdings to maintain target asset allocations. This is the core feature of robo-advisors (Wealthfront, Betterment) and Robinhood Strategies. Agents performing rebalancing must handle drift thresholds, tax-aware execution, wash sale avoidance, minimum trade sizes, and settlement timing. Incorrect rebalancing generates unnecessary tax events, triggers wash sales, or drifts from the target allocation.

## The Problem

An agent that rebalances naively -- selling overweight positions and buying underweight ones -- will: (1) generate capital gains tax events on every rebalance, (2) trigger wash sales if selling at a loss and buying similar securities within 30 days, (3) execute trades so small that commissions and tax impact exceed the benefit, (4) attempt to rebalance again before prior trades settle, creating GFV in cash accounts, and (5) ignore the tax advantage of placing tax-inefficient assets in tax-advantaged accounts (asset location).

## Rules

1. **Drift threshold rebalancing.** Trigger rebalancing when any asset class deviates from its target allocation by more than the threshold. Common thresholds: ~5% absolute OR ~20% relative (Wealthfront uses whichever triggers first). Example: if target is 60% stocks and current is 66%, that's 6% absolute drift or 10% relative drift.

2. **Calendar rebalancing.** Alternative approach: rebalance on a fixed schedule (quarterly, semi-annually, annually). Simpler but may allow excessive drift between dates or trigger unnecessary trades when allocations are within tolerance. Modern robo-advisors (Betterment, Wealthfront) use hybrid drift+calendar — continuous drift monitoring with a daily or intraday check, plus a calendar floor to catch slow-moving drift. Pure calendar rebalancing is considered legacy.

3. **Cash-flow rebalancing.** Use incoming deposits and withdrawals to move toward target allocations without selling. This is the most tax-efficient approach. Direct new deposits to underweight asset classes. Use withdrawals from overweight classes.

4. **Tax-aware rebalancing.** When selling to rebalance: (a) prioritize selling positions with losses (tax-loss harvesting), (b) use specific tax lot identification to minimize gains, (c) prefer selling long-term gains over short-term gains, (d) consider the net tax impact before executing.

5. **Wash sale interaction.** If rebalancing sells a position at a loss, the agent must NOT buy substantially identical securities within 30 days. This is critical when rebalancing across multiple accounts or when DCA buys overlap with rebalance sells.

6. **Tolerance bands.** Use two-tier thresholds: inner band (no action needed, e.g. +/-3%) and outer band (urgent rebalance needed, e.g. +/-10%). This prevents constant micro-rebalancing while catching large drifts.

7. **Minimum trade size.** Do not execute rebalance trades below a minimum dollar amount. Industry standard minimums: $10-$50 per trade (Betterment uses ~$10, Wealthfront ~$50). A $2 rebalance trade generates a taxable event with zero practical benefit. The tax cost of the trade may exceed the drift reduction benefit.

8. **Settlement timing.** After a rebalance, the agent cannot rebalance again until prior trades settle (T+1 for US equities since May 28, 2024). In cash accounts, attempting to rebalance with unsettled funds causes a Good Faith Violation — see `trading/regulations/good-faith-violations/rules` for the 3-strike rule and enforcement details.

9. **Asset location.** Place tax-inefficient assets (bonds, REITs, high-dividend stocks) in tax-advantaged accounts (IRA, 401k). Place tax-efficient assets (growth stocks, index ETFs) in taxable accounts. Rebalancing should respect account type.

## Examples

### Drift calculation
```python
def calculate_drift(
    target_allocations: dict[str, float],
    current_allocations: dict[str, float],
) -> dict[str, float]:
    """Calculate absolute drift per asset class."""
    drift = {}
    for asset_class, target_pct in target_allocations.items():
        current_pct = current_allocations.get(asset_class, 0)
        drift[asset_class] = current_pct - target_pct
    return drift

# Example:
# target:  {"us_stocks": 60, "intl_stocks": 25, "bonds": 15}
# current: {"us_stocks": 68, "intl_stocks": 20, "bonds": 12}
# drift:   {"us_stocks": +8, "intl_stocks": -5, "bonds": -3}
# If threshold is 5%, us_stocks and intl_stocks trigger rebalance.
```

### Tax-aware sell order
```python
def select_tax_lots_for_rebalance(
    lots: list[dict], target_sell_amount: float
) -> list[dict]:
    """Select tax lots to minimize tax impact during rebalance."""
    # Priority: losses first, then long-term gains, then short-term gains
    lots_sorted = sorted(lots, key=lambda l: (
        0 if l["unrealized_pnl"] < 0 else 1,  # losses first
        0 if l["holding_days"] >= 365 else 1,  # long-term before short-term
        l["unrealized_pnl"],  # smallest gains first
    ))
    selected = []
    remaining = target_sell_amount
    for lot in lots_sorted:
        if remaining <= 0:
            break
        selected.append(lot)
        remaining -= lot["market_value"]
    return selected
```

## Agent Checklist

- [ ] Define target allocations with explicit drift thresholds
- [ ] Use cash-flow rebalancing first before selling to rebalance
- [ ] Check for wash sale conflicts before executing rebalance sells at a loss
- [ ] Set minimum trade size to avoid micro-rebalance tax events
- [ ] Wait for prior rebalance trades to settle before rebalancing again
- [ ] Use specific tax lot identification when selling
- [ ] Respect asset location across account types
- [ ] Log every rebalance decision with before/after allocations

## Structured Checks

```yaml
checks:
  - id: rebalance_drift_check
    condition: "rebalance_threshold_pct == 0 OR max_drift_pct <= rebalance_threshold_pct"
    severity: high
    message: "Portfolio drift exceeds rebalance threshold"
  - id: rebalance_min_trade
    condition: "rebalance_min_trade_usd == 0 OR proposed_trade_usd >= rebalance_min_trade_usd"
    severity: medium
    message: "Proposed rebalance trade below minimum threshold -- tax cost may exceed benefit"
```

## Sources

- Wealthfront Tax-Loss Harvesting White Paper
- Betterment Tax-Coordinated Portfolio Documentation
- Vanguard: Best Practices for Portfolio Rebalancing
- FINRA Investor Education: Portfolio Rebalancing
- IRS Publication 550: Investment Income and Expenses (wash sale rules)
