---
id: "trading/regulations/short-selling/rules"
title: "Short Selling and Reg SHO Compliance"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - short-selling
  - reg-sho
  - locate
  - uptick-rule
  - close-out
  - hard-to-borrow
  - forced-buy-in
  - failure-to-deliver
severity: "CRITICAL"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - order-execution-engines
related:
  - "trading/regulations/margin-requirements/rules"
  - "trading/order-execution/best-execution/gotchas"
---

# Short Selling and Reg SHO Compliance

## Summary

Regulation SHO governs short selling of US equity securities. It requires brokers to locate shares before executing a short sale, imposes close-out deadlines for failures to deliver (FTD), and triggers an alternative uptick rule when a stock drops 10% or more. An agent that shorts without proper locate confirmation, ignores close-out deadlines, or fails to monitor margin requirements will cause Reg SHO violations, forced buy-ins, and potential regulatory action against the broker.

## The Problem

Short selling has more regulatory requirements than going long. An agent that treats short positions like inverted long positions will miss: (1) the locate requirement -- you cannot short a stock without your broker confirming shares are available to borrow, (2) the alternative uptick rule that restricts short selling on stocks that dropped 10%+, (3) close-out deadlines that force the broker to buy shares on your behalf (at any price), (4) escalating borrow costs that can exceed the trade's profit potential, and (5) dividend obligations where the short seller must pay dividends to the lender.

## Rules

1. **Locate requirement (Rule 203(b)(1)).** Before accepting a short sale order, the broker must have reasonable grounds to believe the security can be borrowed and delivered by settlement date. The agent must confirm locate status before submitting short orders.

2. **Alternative uptick rule (Rule 201).** When a stock declines 10% or more from the prior day's close, short selling is restricted to prices above the national best bid (NBBB) for the remainder of the current trading day AND the entire following trading day. This is a circuit breaker — the restriction lasts approximately 1.5 trading days from trigger.

3. **Threshold securities list.** Stocks with aggregate FTD of 10,000+ shares for 5+ consecutive settlement days are placed on the threshold securities list (published daily by each SRO). Short positions in threshold securities must be closed out by T+3 after settlement date (13 consecutive settlement days on the list). The SEC threshold securities list is available at https://www.sec.gov/data/foiadocsfailsdatahtm.

4. **Close-out deadlines.** Regular securities: T+2 for FTD. Threshold securities: T+1. If the broker fails to deliver by the deadline, they must buy shares in the open market (forced buy-in).

5. **Forced buy-in.** The broker can (and will) buy shares to close your short position at any time if: (a) shares become unavailable to borrow, (b) close-out deadline is missed, or (c) the lender recalls their shares. This happens at market price with no warning.

6. **Hard-to-borrow (HTB) fees.** Borrowing shares incurs a daily cost (annualized rate). HTB rates can change daily without notice. Rates above 50% annualized are common for heavily shorted stocks and can exceed the trade's expected profit.

7. **Margin requirements.** Initial margin: 150% of short sale value (Reg T). Maintenance margin: 130% of current market value (FINRA). If the stock rises, the margin requirement increases and may trigger a margin call.

8. **Dividend payment obligation.** If you are short through the ex-dividend date, you owe the dividend payment to the share lender. This is a cash outflow the agent must account for.

9. **Naked short selling prohibition.** Selling short without a locate (naked shorting) is illegal. It creates a failure to deliver and can result in regulatory action.

10. **Broker-specific locate APIs.** Interactive Brokers provides real-time locate via their API (`reqSecDefOptParams` for borrow availability). Most retail brokers (Robinhood, Alpaca) do not expose locate APIs — short selling is either handled internally or not supported for retail accounts. Agents must verify broker capabilities before implementing automated short strategies.

## Examples

### Locate workflow
```python
def submit_short_order(broker_api, symbol: str, quantity: int) -> dict:
    """Always obtain locate before shorting."""
    # Step 1: Request locate
    locate = broker_api.request_locate(symbol, quantity)
    if not locate.available:
        raise ValueError(f"Cannot short {symbol}: no shares available to borrow")

    # Step 2: Check borrow rate
    if locate.borrow_rate_annualized > 100:
        raise ValueError(
            f"Borrow rate for {symbol} is {locate.borrow_rate_annualized}% "
            f"-- exceeds risk threshold"
        )

    # Step 3: Submit order with locate reference
    return broker_api.submit_order(
        symbol=symbol,
        side="sell_short",
        quantity=quantity,
        locate_id=locate.id,
    )
```

### Margin calculation
```
Short sell 100 shares of XYZ at $50:
  Short sale proceeds: $5,000
  Initial margin required: $5,000 * 150% = $7,500
  Maintenance margin: current_price * 100 * 130%

If XYZ rises to $60:
  Maintenance: $60 * 100 * 130% = $7,800
  Unrealized loss: ($60 - $50) * 100 = $1,000
  If account equity < $7,800 -> margin call
```

### Uptick rule scenario
```
Prior close: $100.00
Current price: $89.50 (down 10.5% -> Rule 201 triggered)

Short sell orders restricted to prices > national best bid.
If best bid is $89.50, short orders must be at $89.51 or higher.
This restriction lasts until the end of the NEXT trading day.
```

## Agent Checklist

- [ ] Always confirm locate before submitting short sale orders
- [ ] Check if symbol is on the threshold securities list
- [ ] Monitor borrow rate daily -- rates change without notice
- [ ] Calculate margin requirement using current market value, not entry price
- [ ] Check for Rule 201 circuit breaker before submitting short orders
- [ ] Account for dividend payment obligations on ex-dates
- [ ] Set alerts for forced buy-in risk when shares become hard to borrow
- [ ] Track close-out deadlines for any FTD situations

## Structured Checks

```yaml
checks:
  - id: short_locate_required
    condition: "short_positions_count == 0 OR all_shorts_have_locate == 'true'"
    severity: critical
    message: "Short position without locate -- Reg SHO violation"
  - id: short_margin_maintenance
    condition: "short_positions_count == 0 OR short_margin_ratio >= 0.30"
    severity: critical
    message: "Short position below 130% maintenance margin -- forced buy-in risk"
```

## Sources

- SEC Regulation SHO: https://www.sec.gov/rules/final/34-50103.htm
- FINRA Rule 4210 (Margin Requirements): https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210
- SEC Rule 201 (Alternative Uptick Rule): https://www.sec.gov/rules/final/2010/34-61595.pdf
- SEC Threshold Securities List: https://www.sec.gov/rules/final/34-50103.htm#threshold
- FINRA Short Interest Reporting: https://www.finra.org/filing-reporting/short-interest
