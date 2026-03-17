---
id: "trading/regulations/pdt-rule/rules"
title: "Pattern Day Trader (PDT) Rule"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - pdt
  - day-trading
  - margin
  - finra
  - sec
severity: "CRITICAL"
last_verified: "2026-03-01"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - order-execution-engines
related:
  - "trading/broker-apis/alpaca/quirks"
  - "trading/market-structure/trading-hours/reference"
---

# Pattern Day Trader (PDT) Rule

## Summary

The Pattern Day Trader rule is a FINRA regulation (Rule 4210) that restricts accounts with less than $25,000 in equity from making 4 or more day trades within a rolling 5-business-day window when using a margin account. Violation triggers a 90-day trading restriction or a margin call. This rule is one of the most common causes of trading agent failures and unexpected account freezes.

## The Problem

A trading agent that does not track its day trade count across sessions will eventually trigger a PDT violation. This is especially dangerous because: (1) the count persists across sessions — restarting the agent does not reset it, (2) the 5-day window is rolling, not calendar-based, (3) brokers enforce this even in paper trading environments, and (4) the consequence is severe — a 90-day freeze on the account. An agent making 2 round-trip trades per day will hit the limit in just 2 days.

## Rules

1. **Definition of a day trade.** A day trade is the purchase and sale (or short sale and cover) of the same security on the same trading day in a margin account. Opening a position at 10:00 AM and closing it at 3:00 PM on the same day = 1 day trade.

2. **The PDT threshold: 4 day trades in 5 business days.** If an account executes 4 or more day trades within any rolling 5-business-day period AND those day trades represent more than 6% of total trades in that period, the account is flagged as a Pattern Day Trader.

3. **Equity requirement: $25,000 minimum.** Once flagged as PDT, the account must maintain at least $25,000 in equity (cash + securities) at all times. If equity drops below $25,000, the account cannot day trade until the minimum is restored.

4. **Consequences of violation:**
   - Margin call requiring deposit to bring equity above $25,000
   - 90-day restriction to cash-only trading if the margin call is not met within 5 business days
   - Some brokers freeze the account entirely rather than restricting to cash

5. **The rolling window is 5 BUSINESS days, not calendar days.** Weekends and market holidays do not count. A day trade on Monday and 3 on the following Monday (with a holiday on Friday) may still be within the same 5-business-day window.

6. **Each leg of a multi-leg strategy counts separately.** If you buy 100 shares at 10 AM, sell 50 at 11 AM, and sell 50 at 2 PM — that is ONE day trade (one open, one close of the same position). But buying 100 AAPL and 100 MSFT, then selling both same day = TWO day trades.

7. **Cash accounts are exempt but have T+2 settlement.** Cash accounts (non-margin) are NOT subject to PDT. However, stock sale proceeds take 2 business days to settle (T+2). Trading with unsettled funds triggers a Good Faith Violation. After 3 GFV in 12 months, the account is restricted to settled-cash trading for 90 days.

8. **The agent MUST persist day trade count across restarts.** The most common agent mistake is tracking day trades in memory only. When the agent restarts, it loses count and may immediately violate PDT.

## Examples

### Day trade count tracking
```python
from datetime import date, timedelta
from collections import deque

class PDTTracker:
    def __init__(self, equity: float, is_margin: bool = True):
        self.equity = equity
        self.is_margin = is_margin
        # Store as (business_date, ticker) tuples
        self.day_trades = deque()  # Must be persisted to disk/DB!

    def record_day_trade(self, ticker: str, trade_date: date):
        self.day_trades.append((trade_date, ticker))
        self._prune_old_trades(trade_date)

    def _prune_old_trades(self, current_date: date):
        """Remove trades outside the 5-business-day window."""
        cutoff = self._subtract_business_days(current_date, 5)
        while self.day_trades and self.day_trades[0][0] < cutoff:
            self.day_trades.popleft()

    def can_day_trade(self) -> bool:
        if not self.is_margin:
            return True  # Cash accounts exempt
        if self.equity >= 25000:
            return True  # Above PDT equity threshold
        return len(self.day_trades) < 3  # Allow up to 3, block the 4th

    def remaining_day_trades(self) -> int:
        if not self.is_margin or self.equity >= 25000:
            return float('inf')
        return max(0, 3 - len(self.day_trades))

    @staticmethod
    def _subtract_business_days(d: date, n: int) -> date:
        current = d
        while n > 0:
            current -= timedelta(days=1)
            if current.weekday() < 5:  # Mon-Fri
                n -= 1
        return current
```

### Scenario: accidental PDT violation
```
Monday:    Buy 100 AAPL at 10:00, sell at 14:00  -> Day trade #1
Tuesday:   Buy 50 TSLA at 09:35, sell at 11:00   -> Day trade #2
Wednesday: Buy 200 SPY at 10:30, sell at 15:30    -> Day trade #3
Thursday:  Buy 100 NVDA at 09:45, sell at 12:00   -> Day trade #4 (PDT VIOLATION!)

Account equity: $18,000 (below $25k threshold)
Result: Account flagged as PDT, margin call issued.
If not resolved in 5 business days: 90-day cash-only restriction.
```

### Cash account workaround with settlement tracking
```python
class CashAccountTracker:
    """Track settled funds to avoid Good Faith Violations."""

    def __init__(self, cash_balance: float):
        self.settled_cash = cash_balance
        self.pending_settlements = []  # (settlement_date, amount)

    def sell(self, amount: float, trade_date: date):
        # Proceeds settle T+2 (2 business days after trade)
        settlement_date = self._add_business_days(trade_date, 2)
        self.pending_settlements.append((settlement_date, amount))

    def available_to_trade(self, current_date: date) -> float:
        # Settle any matured proceeds
        for sdate, amount in self.pending_settlements[:]:
            if sdate <= current_date:
                self.settled_cash += amount
                self.pending_settlements.remove((sdate, amount))
        return self.settled_cash
```

### Multiple broker workaround
```
Broker A (margin, $15k equity): 3 day trades max per 5 business days
Broker B (margin, $12k equity): 3 day trades max per 5 business days
Combined: 6 day trades per 5 business days across both accounts

This is legal — PDT is enforced per account, not per person.
However, each account independently tracks its own count.
```

## Agent Checklist

- [ ] Track day trade count in persistent storage (database or file), never only in memory
- [ ] Before every same-day close, check `remaining_day_trades() > 0`
- [ ] Know whether the account is margin or cash
- [ ] If cash account, track T+2 settlement to avoid Good Faith Violations
- [ ] Query current account equity before each trading session
- [ ] Count business days correctly (exclude weekends and market holidays)
- [ ] Log every day trade with timestamp for audit trail
- [ ] Handle the broker's PDT flag — query account status via API before trading
- [ ] Test PDT tracking in paper trading (most brokers enforce it there too)

## Structured Checks

```yaml
checks:
  - id: pdt_count_check
    condition: "day_trades_count_5d < 4 OR account_type == 'cash' OR equity >= 25000"
    severity: critical
    message: "PDT violation: 4th day trade on margin account under $25k"
  - id: pdt_equity_warning
    condition: "equity >= 25000 OR account_type == 'cash'"
    severity: high
    message: "Margin account equity below $25k PDT threshold"
  - id: pdt_margin_awareness
    condition: "account_type == 'cash' OR equity >= 25000 OR day_trades_count_5d < 3"
    severity: medium
    message: "Approaching PDT limit: 3 day trades on margin account under $25k"
```

## Sources

- FINRA Rule 4210 (Margin Requirements): https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210
- FINRA Day-Trading Margin Requirements: https://www.finra.org/investors/investing/investment-products/day-trading
- SEC Investor Bulletin on Day Trading: https://www.sec.gov/investor/pubs/daytips.htm
- T+2 Settlement (SEC Rule 15c6-1): https://www.sec.gov/rules/final/2017/34-80295.pdf
