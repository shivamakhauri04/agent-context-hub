---
id: "trading/corporate-actions/stock-splits/handling"
title: "Stock Split Detection and Handling"
domain: "trading"
version: "1.0.0"
category: "corporate-actions"
tags:
  - stock-splits
  - corporate-actions
  - aapl
  - price-adjustment
severity: "CRITICAL"
last_verified: "2026-03-01"
applies_to:
  - trading-agents
  - backtesting-systems
  - order-management-systems
related:
  - "trading/data-vendors/yfinance/gotchas"
  - "trading/data-vendors/polygon/gotchas"
---

# Stock Split Detection and Handling

## Summary

Stock splits (forward and reverse) change a security's share count and price without altering the total market value of a position. They are one of the most dangerous events for trading agents because they look like extreme price moves in raw data, they cause historical data to be retroactively adjusted by data providers, and they require immediate updates to all pending orders and position tracking. An agent that does not handle splits will interpret a 4:1 split as a 75% crash and may panic-sell or trigger false risk alerts.

## The Problem

When Apple executed its 4:1 forward split on August 31, 2020, the stock price dropped from ~$500 to ~$125 overnight. An agent monitoring for large price drops would see a -75% move and potentially liquidate the position, trigger stop losses, or flag a risk event. Meanwhile, data providers like yfinance retroactively adjust ALL historical prices by dividing by 4, which means previously stored prices no longer match fresh downloads. Limit orders set at pre-split prices become nonsensical post-split.

## Rules

1. **Forward splits multiply shares and divide price.** In a 4:1 split (e.g., AAPL Aug 2020), each shareholder receives 4 shares for every 1 held. The price divides by 4. Position value is unchanged: 100 shares at $500 = 400 shares at $125 = $50,000.

2. **Reverse splits divide shares and multiply price.** In a 1:8 reverse split (e.g., GE Aug 2021), every 8 shares become 1 share. Price multiplies by 8. GE went from ~$13 to ~$104 overnight. These are often done by companies trying to avoid delisting (exchanges require minimum price, usually $1).

3. **Detect splits before reacting to overnight price gaps.** An overnight price change of 50%+ that coincides with a whole-number ratio (2:1, 3:1, 4:1, 10:1 forward, or 1:5, 1:8, 1:10 reverse) is almost certainly a split, not a crash or spike. The agent should:
   - Check a corporate actions API or news feed
   - Verify that `new_price * split_ratio ≈ old_price`
   - Verify that `new_shares / split_ratio ≈ old_shares`

4. **Data providers adjust prices retroactively.** After a 4:1 split, yfinance, Polygon, and most providers divide ALL historical close prices by 4. This means:
   - Stored historical data from before the split no longer matches fresh downloads
   - Backtesting on stored data vs. fresh data will produce different results
   - Technical indicators computed on pre-adjustment data are invalid post-split

5. **All pending orders must be adjusted after a split.** A limit buy at $490 (pre-split) must become $122.50 (post-split for 4:1). Most brokers handle this automatically for GTC orders, but agent-managed orders in a local order book MUST be manually adjusted.

6. **Position sizes must be updated.** After a 4:1 split, if the agent tracks 100 shares, it must update to 400 shares. The cost basis per share must be divided by 4.

7. **Reverse splits can create fractional shares.** If you hold 10 shares of a stock that does a 1:8 reverse split, you would get 1.25 shares. Most brokers pay out fractional shares in cash. The agent must handle this fractional liquidation.

8. **Options contracts are adjusted after splits.** A call option with a $500 strike on AAPL pre-split becomes a $125 strike post-split, and the contract multiplier changes. Non-standard split-adjusted options can have unusual contract sizes.

## Examples

### Real split events for reference
```
AAPL 4:1 Forward Split — August 31, 2020
  Pre-split close (Aug 28): $499.23
  Post-split open (Aug 31): $127.58
  100 shares at $499.23 -> 400 shares at $127.58

TSLA 3:1 Forward Split — August 25, 2022
  Pre-split close (Aug 24): $891.29
  Post-split open (Aug 25): $302.36
  50 shares at $891.29 -> 150 shares at $302.36

GOOGL 20:1 Forward Split — July 18, 2022
  Pre-split close (Jul 15): $2,168.78
  Post-split open (Jul 18): $108.67
  10 shares at $2,168.78 -> 200 shares at $108.67

GE 1:8 Reverse Split — August 2, 2021
  Pre-split close (Jul 30): $12.95
  Post-split open (Aug 2): $104.56
  800 shares at $12.95 -> 100 shares at $104.56

AMZN 20:1 Forward Split — June 6, 2022
  Pre-split close (Jun 3): $2,447.00
  Post-split open (Jun 6): $124.79
```

### Split detection logic
```python
from datetime import date

def detect_potential_split(
    ticker: str,
    prev_close: float,
    current_open: float,
    prev_shares: int
) -> dict | None:
    """Detect if an overnight price change is likely a stock split."""
    if prev_close == 0 or current_open == 0:
        return None

    ratio = prev_close / current_open

    # Common forward split ratios
    forward_ratios = [2, 3, 4, 5, 10, 15, 20, 25, 50]
    # Common reverse split ratios
    reverse_ratios = [1/2, 1/3, 1/4, 1/5, 1/8, 1/10, 1/15, 1/20]

    for r in forward_ratios:
        if abs(ratio - r) / r < 0.05:  # Within 5% tolerance
            return {
                "type": "forward",
                "ratio": f"{r}:1",
                "new_shares": int(prev_shares * r),
                "new_cost_basis_multiplier": 1 / r,
            }

    for r in reverse_ratios:
        inv = 1 / r
        if abs(ratio - r) / abs(r) < 0.05:
            return {
                "type": "reverse",
                "ratio": f"1:{int(inv)}",
                "new_shares": prev_shares / int(inv),
                "new_cost_basis_multiplier": int(inv),
            }

    return None  # Not a recognizable split ratio — may be a real crash
```

### Adjusting orders and positions after a split
```python
def adjust_for_split(position: dict, split_ratio: float) -> dict:
    """
    Adjust position after a forward split.
    split_ratio: number of new shares per old share (e.g., 4 for a 4:1 split)
    """
    return {
        "ticker": position["ticker"],
        "shares": int(position["shares"] * split_ratio),
        "cost_basis_per_share": position["cost_basis_per_share"] / split_ratio,
        "total_cost_basis": position["total_cost_basis"],  # Unchanged!
    }

def adjust_orders_for_split(orders: list[dict], split_ratio: float) -> list[dict]:
    """Adjust all pending orders after a forward split."""
    adjusted = []
    for order in orders:
        adjusted.append({
            **order,
            "limit_price": order.get("limit_price", 0) / split_ratio if order.get("limit_price") else None,
            "stop_price": order.get("stop_price", 0) / split_ratio if order.get("stop_price") else None,
            "quantity": int(order["quantity"] * split_ratio),
        })
    return adjusted

# Example: AAPL 4:1 split
position = {"ticker": "AAPL", "shares": 100, "cost_basis_per_share": 300, "total_cost_basis": 30000}
adjusted = adjust_for_split(position, 4.0)
# {"ticker": "AAPL", "shares": 400, "cost_basis_per_share": 75.0, "total_cost_basis": 30000}
```

## Agent Checklist

- [ ] Before reacting to any overnight price drop >40%, check for a stock split announcement
- [ ] Maintain a corporate actions calendar or subscribe to a corporate actions API feed
- [ ] After detecting a split, adjust: share count, cost basis per share, limit orders, stop losses
- [ ] Handle fractional shares from reverse splits (most brokers pay cash-in-lieu)
- [ ] If using stored historical data, mark it with the adjustment date and re-download after splits
- [ ] For backtesting, decide on split-adjusted vs. unadjusted data and be consistent
- [ ] Verify that `total_position_value` is approximately unchanged after adjustment (sanity check)
- [ ] Log all split adjustments with before/after values for audit trail
- [ ] Check options positions separately — strike prices and contract sizes change

## Sources

- NYSE Listed Company Manual Section 703: Stock Splits
- FINRA Corporate Actions notifications: https://www.finra.org/filing-reporting/corporate-actions
- SEC EDGAR 8-K filings (stock splits are disclosed as material events)
- Apple Investor Relations, 4:1 split announcement: https://investor.apple.com
- GE Investor Relations, 1:8 reverse split announcement: https://www.ge.com/investor-relations
