---
id: "trading/market-structure/t1-settlement/reference"
title: "T+1 Settlement Reference"
domain: "trading"
version: "1.0.0"
category: "market-structure"
tags:
  - settlement
  - t-plus-1
  - sec-rule-15c6
  - buying-power
  - options-exercise
  - corporate-actions
  - failed-trades
severity: "HIGH"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - order-execution-engines
  - settlement-systems
related:
  - "trading/regulations/pdt-rule/rules"
  - "trading/regulations/wash-sale/rules"
---

# T+1 Settlement Reference

## Summary

US equities and corporate bonds moved from T+2 to T+1 settlement on May 28, 2024 (SEC Rule 15c6-1(a)). Trade date plus one business day. This affects cash account buying power, options exercise/assignment timing, margin call deadlines, corporate action record/ex-dates, and failed trade resolution. Any agent with hardcoded "T+2" or `settlement_days = 2` is NOW WRONG and will miscalculate buying power, settlement dates, and corporate action eligibility.

## The Problem

Agents built before May 2024 often have T+2 hardcoded in settlement calculations. This causes: (1) cash account buying power restored one day late (users can't trade when they should be able to), (2) options exercise/assignment settlement dates calculated wrong (1 day late), (3) margin call deadlines too generous (more time assumed than actually available), (4) corporate action record/ex-date calculations off by one day, (5) failed trade detection logic miscalibrated. The most insidious form is when T+2 is buried in a constant or config that was never updated.

## Rules

1. **T+1 effective May 28, 2024.** SEC Rule 15c6-1(a) shortened the standard settlement cycle for most securities from T+2 to T+1. This is not optional — all US broker-dealers must comply.

2. **Cash account buying power restored T+1.** When a stock is sold in a cash account, the proceeds are available for trading the next business day (T+1). Previously, this was two business days (T+2). Agents that still calculate T+2 are delaying buying power restoration by one day.

3. **Options exercise/assignment settles T+1.** When an option is exercised or assigned, the resulting stock position settles T+1 from the exercise date. Tighter deadlines mean less time to manage exercise-related positions and cash requirements.

4. **Margin call resolution: less time.** With T+1, the timeline for resolving margin calls is compressed. Brokers issue margin calls based on settlement dates, and the shorter cycle means less time to deposit funds or liquidate positions.

5. **Corporate actions: record and ex-date now 1 business day apart.** Under T+2, the ex-date was 2 business days before the record date. Under T+1, the ex-date is 1 business day before the record date. Agents calculating ex-dates from record dates (or vice versa) must use the correct offset.

6. **Failed trade rates.** The shorter settlement window increases the risk of failed trades (delivery failures). Agents should monitor for settlement failures and have retry/escalation logic.

7. **AUDIT: any hardcoded T+2 is NOW WRONG.** Search your codebase for:
   - `settlement_days = 2`
   - `T+2` in comments or constants
   - `timedelta(days=2)` in settlement contexts
   - Any `+ 2` in date calculations related to settlement
   All of these should be updated to 1 (or use a configurable constant).

8. **Exceptions — not everything is T+1:**
   - US government securities: T+0 (same-day settlement, effective May 2025)
   - Some corporate bonds: may still be T+2
   - Municipal bonds: T+1 (changed with equities)
   - Options: T+1 (changed with equities)
   - Mutual funds: varies, often T+1 or T+2

9. **Business days only.** Settlement is measured in business days. A trade executed Friday afternoon settles Monday (T+1). A trade executed before a Monday holiday settles Tuesday.

10. **Impact on wash sale calculations.** The wash sale 30-day window uses calendar days (not settlement days), so T+1 does not change wash sale calculations. However, the settlement date determines when shares are actually delivered, which affects position tracking.

## Examples

### Cash account buying power
```
T+2 (old, WRONG):
Monday: Sell $10,000 of AAPL
Tuesday: Funds still settling
Wednesday: $10,000 available to trade

T+1 (current, CORRECT):
Monday: Sell $10,000 of AAPL
Tuesday: $10,000 available to trade (one day sooner)
```

### Corporate action ex-date calculation
```
Record date: March 20 (Thursday)

T+2 (old, WRONG):
Ex-date: March 18 (Tuesday) — 2 business days before record date

T+1 (current, CORRECT):
Ex-date: March 19 (Wednesday) — 1 business day before record date

Agent using T+2 logic would set ex-date one day too early,
potentially causing incorrect dividend eligibility calculations.
```

### Options exercise settlement
```
Friday: Long call option exercised (ITM at expiration)

T+2 (old, WRONG):
Stock delivered: Tuesday (T+2 from Friday)
Must have cash/margin by: Tuesday

T+1 (current, CORRECT):
Stock delivered: Monday (T+1 from Friday)
Must have cash/margin by: Monday — ONE LESS DAY to prepare
```

### Code audit checklist
```python
# WRONG — search for and fix these patterns:
SETTLEMENT_DAYS = 2  # Should be 1
settlement_date = trade_date + timedelta(days=2)  # Should be 1
buying_power_available = trade_date + BDay(2)  # Should be BDay(1)
ex_date = record_date - timedelta(days=2)  # Should be 1

# CORRECT:
SETTLEMENT_DAYS = 1
settlement_date = trade_date + BDay(1)
buying_power_available = trade_date + BDay(1)
ex_date = record_date - BDay(1)
```

## Agent Checklist

- [ ] AUDIT: Search codebase for any hardcoded T+2 / `settlement_days = 2` and update to T+1
- [ ] Cash accounts: restore buying power T+1, not T+2
- [ ] Options exercise/assignment: calculate settlement as T+1
- [ ] Corporate actions: ex-date is 1 business day before record date, not 2
- [ ] Margin calls: adjust deadline calculations for shorter settlement cycle
- [ ] Use a configurable constant for settlement days (not hardcoded) for future changes
- [ ] Handle government securities separately (T+0 since May 2025)
- [ ] Account for business days only (skip weekends and holidays)

## Structured Checks

```yaml
checks:
  - id: settlement_cycle_check
    condition: "settlement_days <= 1 OR settlement_days_override == 'true'"
    severity: high
    message: "Settlement cycle uses T+2 or higher — US equities settled T+1 since May 2024"
```

## Sources

- SEC Rule 15c6-1(a) — Shortening the Settlement Cycle: https://www.sec.gov/rules/final/2023/34-97142.pdf (accessed 2026-03-15)
- SEC Press Release — T+1 Settlement (Feb 2023): https://www.sec.gov/news/press-release/2023-29 (accessed 2026-03-15)
- DTCC T+1 Resource Center: https://www.dtcc.com/ust1 (accessed 2026-03-15)
- SEC Rule 15c6-2 — Government Securities T+0: https://www.sec.gov/rules/final/2024/34-99615.pdf (accessed 2026-03-15)
