---
id: "trading/portfolio-management/recurring-investments/rules"
title: "Recurring Investments and Dollar-Cost Averaging (DCA)"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - recurring-investment
  - dca
  - dollar-cost-averaging
  - fractional-shares
  - scheduling
  - wash-sale
severity: "HIGH"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - robo-advisors
related:
  - "trading/regulations/wash-sale/rules"
  - "trading/regulations/good-faith-violations/rules"
  - "trading/market-structure/fractional-shares/gotchas"
---

# Recurring Investments and Dollar-Cost Averaging (DCA)

## Summary

Recurring investments (DCA) are the most popular retail feature across all major brokers. The agent configures automatic purchases of specified securities at regular intervals (daily, weekly, biweekly, monthly). While conceptually simple, agents managing DCA must handle insufficient funds, wash sale interaction with tax-loss harvesting, fractional share support, holiday scheduling, and DRIP overlap. Getting these wrong results in failed orders, unintended wash sales, or account restrictions.

## The Problem

An agent that sets up recurring investments without considering the full picture will: (1) trigger recurring buys when the account has insufficient funds, causing failed orders or overdrafts, (2) create wash sales when DCA buys overlap with loss sales in the same or related accounts within 30 days, (3) assume fractional shares are available for all securities (they're not -- some brokers/securities don't support them), (4) miss scheduled buys on holidays without rescheduling, and (5) double-buy when DRIP reinvestment overlaps with recurring purchases of the same security.

## Rules

1. **DCA frequency options.** Common frequencies: daily, weekly, biweekly, monthly. Daily DCA combined with tax-loss harvesting (TLH) is the highest wash sale risk combo — every single buy creates a 30-day conflict window, making it nearly impossible to harvest losses without triggering a wash sale. Flag this combination explicitly to users.

2. **Insufficient funds handling.** When the account lacks funds for a scheduled buy, the agent must decide: skip (try again next interval), retry (try again in 1-3 days), partial fill (buy what you can afford), or cancel (stop the recurring schedule). Most brokers skip and try next interval.

3. **Holiday and weekend scheduling.** If a recurring buy falls on a weekend or market holiday, execute on the next business day. Do not skip entirely. Keep a market holiday calendar updated annually.

4. **Fractional share requirements.** Not all brokers support fractional shares. Not all securities are eligible for fractional trading even at brokers that support it (e.g. OTC stocks, some ETFs). Verify fractional eligibility before setting up small-dollar recurring buys.

5. **Wash sale interaction.** This is the most critical risk. If the agent also performs tax-loss harvesting (TLH), a DCA buy within 30 days of a TLH sell of the same or substantially identical security triggers a wash sale, disallowing the loss deduction. The agent must coordinate TLH and DCA schedules.

6. **DRIP interaction.** Dividend Reinvestment Plans (DRIP) automatically buy more shares on dividend payment dates. If the agent also has a recurring buy for the same security, both execute, potentially doubling the intended investment. Coordinate DRIP and recurring schedules.

7. **Tax lot tracking.** DCA creates many small tax lots over time. FIFO (first-in, first-out) is the IRS default method if no election is made. Specific identification must be elected at the time of sale, not retroactively — the agent must specify which lot to sell before execution. Track each DCA purchase as a separate lot with date and cost basis.

8. **Order timing.** Brokers execute recurring buys at different times: market open (most common), VWAP window, or closing auction. The agent should know when execution happens to avoid surprises during volatile opens.

9. **Minimum investment amounts.** Vary by broker: $1 at Robinhood, $1 at Vanguard (most ETFs), $5 at Schwab, $10 at Fidelity. The agent must respect broker minimums when configuring recurring amounts. Some brokers also have per-security minimums that differ from the account-level minimum.

10. **Pausing and resuming.** The agent should pause recurring investments during: extended market volatility, cash shortfalls, or when the security is involved in a pending corporate action. Resume when conditions normalize.

## Examples

### Wash sale conflict detection
```python
from datetime import date, timedelta

def check_wash_sale_conflict(
    recurring_symbols: set[str],
    recent_loss_sales: list[dict],
    lookback_days: int = 30,
) -> list[str]:
    """Check if recurring buys conflict with recent loss sales."""
    conflicts = []
    cutoff = date.today() - timedelta(days=lookback_days)

    for sale in recent_loss_sales:
        if sale["pnl"] >= 0:
            continue  # Not a loss sale
        sale_date = date.fromisoformat(sale["date"])
        if sale_date < cutoff:
            continue  # Outside 30-day window
        if sale["symbol"] in recurring_symbols:
            conflicts.append(
                f"{sale['symbol']}: loss sale on {sale['date']} "
                f"conflicts with recurring buy (wash sale risk)"
            )
    return conflicts
```

### Monthly cost estimation
```python
FREQ_MONTHLY_MULTIPLIER = {
    "daily": 21,      # ~21 trading days/month
    "weekly": 4.33,   # ~4.33 weeks/month
    "biweekly": 2.17, # ~2.17 biweekly periods/month
    "monthly": 1,
}

def estimate_monthly_cost(recurring: list[dict]) -> float:
    """Estimate total monthly recurring investment cost."""
    total = 0
    for inv in recurring:
        multiplier = FREQ_MONTHLY_MULTIPLIER.get(inv["frequency"], 1)
        total += inv["amount_usd"] * multiplier
    return total

# Example: $50/week SPY + $100/month VTI = $316.50/month
```

## Agent Checklist

- [ ] Verify sufficient cash before each scheduled buy
- [ ] Check for wash sale conflicts with recent loss sales in all accounts
- [ ] Confirm fractional share eligibility for each security
- [ ] Handle holidays by rescheduling to next business day
- [ ] Coordinate with DRIP to avoid unintended double-buying
- [ ] Track each DCA purchase as a separate tax lot
- [ ] Set up monitoring for failed recurring orders
- [ ] Pause recurring buys when cash balance is consistently insufficient

## Structured Checks

```yaml
checks:
  - id: recurring_sufficient_funds
    condition: "recurring_total_monthly_usd == 0 OR recurring_total_monthly_usd <= cash"
    severity: high
    message: "Monthly recurring investments exceed available cash"
  - id: recurring_wash_sale_conflict
    condition: "recurring_wash_sale_symbols_count == 0"
    severity: high
    message: "Recurring investment symbol overlaps with recent loss sale -- wash sale risk"
```

## Sources

- Robinhood Help Center: Recurring Investments
- Schwab: Automatic Investment Plans
- Wealthfront: Tax-Loss Harvesting and DCA Interaction
- IRS Publication 550: Wash Sales
- FINRA Investor Education: Dollar-Cost Averaging
