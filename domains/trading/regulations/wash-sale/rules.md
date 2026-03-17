---
id: "trading/regulations/wash-sale/rules"
title: "IRS Wash Sale Rule"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - wash-sale
  - tax-loss-harvesting
  - irs
  - cost-basis
severity: "CRITICAL"
last_verified: "2026-03-01"
applies_to:
  - trading-agents
  - tax-loss-harvesting-systems
  - portfolio-management-systems
related:
  - "trading/regulations/pdt-rule/rules"
---

# IRS Wash Sale Rule

## Summary

The IRS wash sale rule (Internal Revenue Code Section 1091) prevents taxpayers from claiming a tax deduction on a security sold at a loss if a "substantially identical" security is purchased within 30 calendar days before or after the sale. The disallowed loss is added to the cost basis of the replacement shares. This rule is the single most common cause of incorrect tax-loss harvesting by trading agents.

## The Problem

Trading agents performing tax-loss harvesting frequently violate the wash sale rule because they (1) only check the 30 days AFTER a loss sale, ignoring the 30 days BEFORE, (2) do not recognize "substantially identical" securities (e.g., options on the same underlying), (3) fail to track wash sales across multiple accounts held by the same taxpayer or spouse, and (4) do not properly adjust the cost basis of replacement shares. A single missed wash sale can make an agent's entire tax-loss harvesting calculation incorrect.

## Rules

1. **The 61-day window.** The wash sale rule applies if you buy a substantially identical security within a 61-day window: 30 calendar days BEFORE the sale, the day of the sale, and 30 calendar days AFTER the sale. Most agents only check the forward 30 days — this is WRONG.

2. **"Substantially identical" is broader than the same ticker.** The following are considered substantially identical:
   - Same stock (e.g., sell AAPL, buy AAPL)
   - Options on the same underlying (e.g., sell AAPL stock at a loss, buy AAPL call options)
   - Contracts or rights to acquire the same stock
   - Bonds from the same issuer with similar terms
   - **NOT substantially identical:** Different companies in the same sector (sell AAPL, buy MSFT is fine), different index funds tracking different indices (sell S&P 500 fund, buy Total Market fund — generally OK but consult tax advisor)
   - **Same-index ETFs are risky:** SPDR S&P 500 (SPY) vs iShares S&P 500 (IVV) track the same index. The IRS has no definitive guidance, but same-index funds are widely considered substantially identical by tax professionals. Treat them as such.
   - **Mutual fund to ETF of same index:** Selling Vanguard 500 Index Fund and buying VOO (same index) is almost certainly a wash sale.

3. **Spouse purchases trigger wash sale (Rev. Rul. 2008-5).** If you sell a security at a loss and your spouse buys the same or substantially identical security within the 30-day window, the wash sale rule applies. This is per Revenue Ruling 2008-5.

4. **Cross-account applicability.** The wash sale rule applies across ALL accounts owned by the same taxpayer: taxable brokerage, IRA (traditional and Roth), 401(k), and any other accounts. Selling at a loss in a taxable account and buying in an IRA within 30 days triggers a wash sale — and the loss is permanently disallowed (not added to IRA cost basis).

5. **The disallowed loss is NOT gone forever (it is deferred).** When a wash sale occurs, the disallowed loss is added to the cost basis of the replacement shares. This defers the tax benefit to when the replacement shares are eventually sold.

4. **Partial wash sales are possible.** If you sell 100 shares at a loss and buy back only 50 within the window, only 50 shares' worth of loss is disallowed. The other 50 shares' loss is deductible.

5. **The rule applies across ALL accounts.** Selling AAPL at a loss in your taxable brokerage and buying AAPL in your IRA within 30 days triggers a wash sale. This also applies across accounts held by your spouse.

6. **Calendar days, not business days.** The 30-day windows use calendar days, including weekends and holidays. A loss sale on December 15 has a wash sale window from November 15 to January 14.

7. **Dividend reinvestment plans (DRIPs) can trigger wash sales.** If you sell a stock at a loss but have automatic dividend reinvestment that buys shares within the 30-day window, that triggers a wash sale — even though the purchase was automatic.

8. **Year-end is especially dangerous.** Selling at a loss in late December for tax purposes is invalidated if replacement shares are bought in early January. The IRS does not care about the calendar year boundary — only the 30-day windows.

## Examples

### The backward-window mistake agents commonly make
```
Timeline:
  Nov 20: Agent buys 100 shares NVDA at $450
  Dec 10: NVDA drops to $400
  Dec 15: Agent sells 100 shares NVDA at $400 for $5,000 loss

  Agent checks forward 30 days (Dec 15 - Jan 14): no NVDA purchases.
  Agent claims $5,000 tax loss. CORRECT?

  NO! Agent must also check backward 30 days (Nov 15 - Dec 15).
  The Nov 20 purchase of 100 shares at $450 is within the backward window.

  Result: If the agent bought those Nov 20 shares as a new position while
  already holding other NVDA shares that were sold at a loss, this could
  trigger a wash sale. The backward window catches the REPLACEMENT purchase
  that happened BEFORE the loss sale.
```

### Wash sale with cost basis adjustment
```
Jan 5:   Buy 100 TSLA at $250 ($25,000 cost)
Feb 1:   Sell 100 TSLA at $220 ($22,000 proceeds, $3,000 loss)
Feb 15:  Buy 100 TSLA at $225 ($22,500 cost)

Wash sale triggered: Feb 15 purchase is within 30 days of Feb 1 sale.
Disallowed loss: $3,000
Adjusted cost basis of Feb 15 shares: $22,500 + $3,000 = $25,500

When the agent eventually sells the Feb 15 shares:
- If sold at $260: gain = $260*100 - $25,500 = $500 (not $3,500)
- The $3,000 loss is "recovered" through higher cost basis
```

### Agent wash sale tracker
```python
from datetime import date, timedelta
from dataclasses import dataclass

@dataclass
class TradeRecord:
    ticker: str
    trade_date: date
    quantity: int
    price: float
    action: str  # "buy" or "sell"

class WashSaleTracker:
    WINDOW_DAYS = 30

    def __init__(self):
        self.trades: list[TradeRecord] = []  # Must persist!

    def would_trigger_wash_sale(
        self, ticker: str, action: str, trade_date: date
    ) -> bool:
        """Check if a proposed trade would trigger a wash sale."""
        window_start = trade_date - timedelta(days=self.WINDOW_DAYS)
        window_end = trade_date + timedelta(days=self.WINDOW_DAYS)

        if action == "buy":
            # Check if any loss sale of same ticker happened within window
            for t in self.trades:
                if (t.ticker == ticker
                    and t.action == "sell"
                    and self._is_loss_sale(t)
                    and window_start <= t.trade_date <= window_end):
                    return True
        elif action == "sell":
            # Check if any purchase of same ticker within window
            for t in self.trades:
                if (t.ticker == ticker
                    and t.action == "buy"
                    and window_start <= t.trade_date <= window_end):
                    return True  # May trigger wash sale if this sell is at a loss
        return False

    def check_substantially_identical(self, ticker1: str, ticker2: str) -> bool:
        """Check if two tickers are substantially identical.
        This is a simplified check — real implementation needs options mapping."""
        # Same ticker
        if ticker1 == ticker2:
            return True
        # Options on same underlying (simplified)
        base1 = ticker1.split("_")[0] if "_" in ticker1 else ticker1
        base2 = ticker2.split("_")[0] if "_" in ticker2 else ticker2
        return base1 == base2

    def _is_loss_sale(self, trade: TradeRecord) -> bool:
        # Compare against purchase price — requires matching buy lots
        # Implementation depends on cost basis method (FIFO, specific ID)
        pass
```

### Year-end trap
```
Dec 20: Sell 100 AMZN at loss of $4,000 (for tax-loss harvesting)
Jan 3:  Buy 100 AMZN at similar price (to re-establish position)

Result: Wash sale! The $4,000 loss is DISALLOWED for the current tax year.
The loss is added to the cost basis of the Jan 3 shares.

The agent's tax-loss harvesting for the year is completely negated.

Safe alternative: Wait until Jan 20 (31 days) to repurchase AMZN,
or buy a non-substantially-identical alternative (e.g., GOOGL) on Dec 20.
```

## Agent Checklist

- [ ] Check BOTH the 30-day backward AND 30-day forward windows (61 days total)
- [ ] Track all trades across ALL accounts belonging to the same taxpayer
- [ ] Identify substantially identical securities (same stock, options on same underlying)
- [ ] When a wash sale occurs, correctly adjust the cost basis of replacement shares
- [ ] Handle partial wash sales (different quantities in sale vs repurchase)
- [ ] Account for DRIP purchases as potential wash sale triggers
- [ ] Use calendar days, not business days, for the 30-day windows
- [ ] Be especially cautious with trades in late December / early January
- [ ] Persist all trade history — wash sale detection requires at least 61 days of lookback
- [ ] Log wash sale detections with full details for tax reporting (Form 8949)

## Structured Checks

```yaml
checks:
  - id: wash_sale_window_check
    condition: "days_since_loss_sale > 30 OR no_repurchase == 'true'"
    severity: critical
    message: "Potential wash sale: same security repurchased within 30-day window"
  - id: wash_sale_cross_account
    condition: "cross_account_purchases == 0"
    severity: high
    message: "Wash sale risk: same security purchased in another account within window"
  - id: wash_sale_spouse_check
    condition: "spouse_purchases_same_security == 0"
    severity: high
    message: "Wash sale risk: spouse purchased same security within 30-day window"
```

## Sources

- IRS Publication 550, "Investment Income and Expenses" (Chapter 4 — Wash Sales): https://www.irs.gov/publications/p550 (accessed 2026-03-01)
- Internal Revenue Code Section 1091: https://www.law.cornell.edu/uscode/text/26/1091 (accessed 2026-03-01)
- IRS Form 8949 Instructions, "Sales and Other Dispositions of Capital Assets": https://www.irs.gov/forms-pubs/about-form-8949 (accessed 2026-03-01)
- Revenue Ruling 2008-5 (wash sales involving IRAs): https://www.irs.gov/irb/2008-03_IRB#RR-2008-5 (accessed 2026-03-01)
