---
id: "trading/regulations/good-faith-violations/rules"
title: "Good Faith Violations (GFV) in Cash Accounts"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - good-faith-violation
  - gfv
  - cash-account
  - unsettled-funds
  - free-riding
  - settlement
  - t-plus-1
severity: "HIGH"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - order-execution-engines
related:
  - "trading/regulations/pdt-rule/rules"
  - "trading/market-structure/t1-settlement/reference"
---

# Good Faith Violations (GFV) in Cash Accounts

## Summary

A Good Faith Violation occurs when a cash account buys a security using unsettled sale proceeds and then sells that newly purchased security before the original sale proceeds have settled. GFV is the #1 cause of cash account restrictions at retail brokers. Since cash accounts represent the majority of retail accounts (especially at Robinhood), agents operating on cash accounts must track settlement status of every dollar.

## The Problem

An agent that does not track settled vs unsettled cash will inevitably use unsettled proceeds to buy, then sell that position before settlement completes. Three such violations in 12 months results in a 90-day restriction to settled-cash-only trading. The agent effectively freezes the account. Unlike PDT which only applies to margin accounts, GFV is the cash account equivalent and far more common because agents tend to trade frequently.

## Rules

1. **GFV definition.** A GFV occurs when you buy a security with proceeds from a sale that has not yet settled, and then sell that newly purchased security before the original sale settles. The violation is using unsettled funds and then liquidating before settlement.

2. **T+1 settlement (since May 28, 2024).** US equity sale proceeds settle one business day after the trade date (SEC Rule 15c6-1(a) amendment, effective May 28, 2024 — previously T+2). If you sell on Monday, proceeds are available Tuesday. Selling on Friday means proceeds settle Monday. Any hardcoded T+2 logic in legacy systems must be updated.

3. **Free-riding violation.** A more severe form: buying a security, selling it at a profit, and then paying for the original purchase with the sale proceeds. This is illegal under Regulation T and results in a 90-day account freeze on the first occurrence.

4. **3-strike rule.** Three GFV within a rolling 12-month period triggers a 90-day restriction to settled-cash-only trading. The agent cannot use any unsettled proceeds during this period.

5. **Liquidation violation.** Selling an existing position to meet a cash shortfall from a new purchase is a separate violation type at some brokers (distinct from standard GFV). Example: you buy $5,000 of MSFT with only $3,000 settled cash, then sell $2,000 of AAPL to cover the shortfall — this is a liquidation violation even if you don't sell the MSFT. Schwab and Fidelity track this separately from GFV.

6. **Cash accounts vs margin accounts.** GFV applies ONLY to cash accounts. Margin accounts borrow funds from the broker, so settlement timing is irrelevant for trading purposes (but interest accrues). Many agents should consider margin accounts specifically to avoid GFV.

7. **Broker enforcement varies.** Robinhood shows GFV warnings in-app. Schwab restricts after 3 violations. Fidelity may auto-upgrade to margin. Agents must check broker-specific GFV tracking via API.

8. **Agent must track settlement dates.** For every sell order, record the settlement date (trade date + 1 business day). Before any buy order, verify that the cash being used has settled. Never assume all cash is available.

## Examples

### GFV scenario
```
Day 1 (Monday):
  - Sell AAPL for $5,000 (proceeds unsettled until Tuesday)
  - Buy MSFT for $5,000 using unsettled AAPL proceeds
  - Sell MSFT for $5,100 (BEFORE Tuesday)
  -> GFV! Used unsettled funds to buy MSFT, then sold MSFT before AAPL settled.
```

### Safe pattern
```
Day 1 (Monday):
  - Sell AAPL for $5,000 (proceeds unsettled until Tuesday)
  - Buy MSFT for $5,000 using unsettled AAPL proceeds (OK so far)
  - HOLD MSFT until at least Tuesday
Day 2 (Tuesday):
  - AAPL proceeds settle
  - Now safe to sell MSFT
  -> No GFV.
```

### Settlement tracking
```python
from datetime import date, timedelta

def next_business_day(d: date) -> date:
    """T+1 settlement: next business day after trade date."""
    next_d = d + timedelta(days=1)
    while next_d.weekday() >= 5:  # Skip weekends
        next_d += timedelta(days=1)
    return next_d

def can_use_proceeds(sell_date: date, current_date: date) -> bool:
    """Check if sale proceeds have settled."""
    settlement_date = next_business_day(sell_date)
    return current_date >= settlement_date
```

## Agent Checklist

- [ ] Track settled vs unsettled cash separately
- [ ] Before every buy, verify sufficient settled cash OR acknowledge GFV risk
- [ ] Record settlement date for every sell (trade date + 1 business day)
- [ ] Monitor GFV count via broker API -- alert at 2
- [ ] Consider margin account if frequent trading is required
- [ ] Handle weekends and holidays in settlement date calculation
- [ ] Never sell a position bought with unsettled funds before those funds settle

## Structured Checks

```yaml
checks:
  - id: gfv_count_critical
    condition: "account_type != 'cash' OR gfv_count_12m < 3"
    severity: critical
    message: "3+ GFV in 12 months -- cash account restricted to settled-cash trading for 90 days"
  - id: gfv_unsettled_trade
    condition: "account_type != 'cash' OR pending_buy_with_unsettled != 'true'"
    severity: high
    message: "Pending buy uses unsettled funds -- will trigger Good Faith Violation"
```

## Sources

- FINRA Rule 4210 (Margin Requirements) — establishes cash account settlement rules
- FINRA Regulatory Notice: Free-Riding and Good Faith Violations
- SEC Regulation T (12 CFR 220): Credit by Brokers and Dealers
- SEC Rule 15c6-1(a) Amendment (May 28, 2024): T+1 Settlement (previously T+2)
- Robinhood Help Center: Good Faith Violations
- Schwab: Understanding Cash Account Violations
- Fidelity: Cash Account Trading and Settlement
