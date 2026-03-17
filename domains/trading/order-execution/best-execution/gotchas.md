---
id: "trading/order-execution/best-execution/gotchas"
title: "Order Execution and Best Execution Gotchas"
domain: "trading"
version: "1.0.0"
category: "order-execution"
tags:
  - best-execution
  - order-types
  - slippage
  - pfof
  - market-order
  - limit-order
  - stop-loss
severity: "HIGH"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - order-execution-engines
  - algorithmic-trading-systems
related:
  - "trading/broker-apis/alpaca/quirks"
  - "trading/regulations/pdt-rule/rules"
  - "trading/market-structure/trading-hours/reference"
---

# Order Execution and Best Execution Gotchas

## Summary

Order type selection directly impacts execution quality, slippage, and fill rates. Market orders guarantee a fill but NOT a price. Limit orders guarantee a price but NOT a fill. Stop orders become market orders when triggered, exposing them to gap risk. FINRA Rule 5310 requires brokers to seek the most favorable terms for customer orders (best execution). Agents must choose the right order type for each situation and handle partial fills, unfilled orders, and slippage gracefully.

## The Problem

Trading agents that default to market orders in all conditions will experience severe slippage during volatile or illiquid markets. Agents that use only limit orders will face unfilled orders and stale positions. Common failures: (1) placing market orders on illiquid stocks and getting filled at extreme prices, (2) setting stop-losses without understanding gap-down risk, (3) not handling partial fills (receiving 50 of 1000 shares), (4) ignoring odd lot pricing disadvantages, (5) not considering PFOF impact on execution quality.

## Rules

1. **Market Orders: Fill Guaranteed, Price NOT Guaranteed.** A market order executes immediately at the best available price. In normal conditions, slippage is minimal. In volatile or illiquid conditions, slippage can be extreme. An agent placing a market order to buy 10,000 shares of a stock trading 5,000 shares/day will move the price significantly.

2. **Limit Orders: Price Guaranteed, Fill NOT Guaranteed.** A limit order sets the maximum buy price or minimum sell price. The order will only execute at the limit price or better. Risk: the order may never fill if the market moves away. Agents must handle the "unfilled order" state and decide whether to cancel, adjust, or wait.

3. **Stop Orders: Trigger to Market.** A stop order becomes a market order when the stop price is reached. This means:
   - Stop-loss at $50: if stock gaps from $52 to $45 overnight, the stop triggers at market open and executes at ~$45 (not $50)
   - This "gap risk" makes stop orders unreliable as downside protection for volatile or event-driven securities

4. **Stop-Limit Orders: May Never Fill.** A stop-limit order becomes a limit order (not market) when triggered. If the price gaps through both the stop and limit prices, the order will NOT fill at all. The agent thinks it has downside protection but the position remains open.

5. **Partial Fills.** Orders may be partially filled, especially for:
   - Large orders relative to volume
   - Limit orders where only some shares are available at the limit price
   - Multi-leg options orders where legs fill independently

   Agents MUST handle receiving 50 of 1000 shares and decide: wait for the rest, cancel the remainder, or adjust the strategy.

6. **Odd Lots (< 100 shares).** Orders for fewer than 100 shares (odd lots) may not receive NBBO (National Best Bid and Offer) pricing. Market makers are only required to honor quoted prices for round lots (100+ shares). Odd lots may receive slightly worse execution.

7. **Payment for Order Flow (PFOF).** Many zero-commission brokers route retail orders to market makers who pay for the order flow. This means:
   - The broker receives payment for sending your order to a specific venue
   - The market maker may or may not provide price improvement
   - Price improvement is not guaranteed and varies by market maker
   - FINRA Rule 5310 still requires best execution regardless of PFOF arrangements

8. **Best Execution (FINRA Rule 5310).** Brokers must use "reasonable diligence" to seek the most favorable terms for customer orders, considering:
   - Price improvement opportunities
   - Speed of execution
   - Likelihood of execution at quoted size
   - The character of the market for the security

9. **Extended Hours Execution.** Pre-market and after-hours trading has:
   - Wider spreads (less liquidity)
   - Higher slippage risk
   - Limit orders only (most brokers don't allow market orders in extended hours)
   - Lower volume, so large orders have outsized market impact

10. **Time-in-Force Options.** Agents should explicitly set order duration:
    - **DAY**: Expires at market close if unfilled
    - **GTC (Good Till Cancelled)**: Remains active until filled or cancelled (typically up to 90 days)
    - **IOC (Immediate or Cancel)**: Fill immediately or cancel unfilled portion
    - **FOK (Fill or Kill)**: Fill entire order immediately or cancel entirely

## Examples

### Order type selection logic
```python
def select_order_type(
    volatility_percentile: float,
    avg_daily_volume: int,
    order_quantity: int,
    urgency: str,
) -> str:
    volume_ratio = order_quantity / avg_daily_volume if avg_daily_volume > 0 else 1.0

    if urgency == "immediate" and volatility_percentile < 80 and volume_ratio < 0.01:
        return "market"
    if volume_ratio > 0.05:
        return "limit"  # Large order relative to volume — use limit
    if volatility_percentile >= 90:
        return "limit"  # High volatility — control slippage
    return "limit"  # Default to limit for safety
```

### Gap-down stop loss failure
```
Friday close: ACME at $100
Agent sets stop-loss at $95

Weekend: ACME reports accounting fraud

Monday open: ACME opens at $62
Stop triggers at open, executes as market order at ~$62
Agent expected $95 protection, got $62 execution
Actual loss: 38% instead of expected 5%
```

### Partial fill handling
```python
def handle_partial_fill(
    order_id: str,
    requested: int,
    filled: int,
    strategy: str,
) -> str:
    fill_ratio = filled / requested
    if fill_ratio >= 0.90:
        return "accept"  # Close enough, cancel remainder
    if fill_ratio < 0.10 and strategy == "pairs_trade":
        return "cancel_all"  # Too little for strategy to work
    return "wait"  # Let it fill over time
```

## Agent Checklist

- [ ] Default to limit orders — only use market orders for urgent, liquid, low-volatility trades
- [ ] Never use stop orders as reliable downside protection for gap-prone securities
- [ ] Handle partial fills: check filled quantity after every order status update
- [ ] Set explicit time-in-force on every order (never rely on broker defaults)
- [ ] Monitor execution quality: track slippage between expected and actual fill prices
- [ ] For large orders (> 1% of daily volume), use TWAP/VWAP algorithms or limit orders
- [ ] Avoid market orders in pre-market/after-hours sessions
- [ ] Log all order events (submitted, partial fill, filled, cancelled, rejected) with timestamps

## Structured Checks

```yaml
checks:
  - id: market_order_volatility
    condition: "order_type != 'market' OR volatility_percentile < 90"
    severity: high
    message: "Market order during high volatility — consider limit order to control slippage"
  - id: stop_loss_gap_risk
    condition: "order_type != 'stop' OR avg_daily_gap_percent < 3"
    severity: medium
    message: "Stop order on high-gap-risk security — gap-down may execute far below stop price"
```

## Sources

- FINRA Rule 5310 (Best Execution): https://www.finra.org/rules-guidance/rulebooks/finra-rules/5310
- SEC Rule 606 (Order Routing Disclosure): https://www.sec.gov/rules/final/2018/34-84528.pdf
- FINRA Regulatory Notice 15-46 (Best Execution): https://www.finra.org/rules-guidance/notices/15-46
- SEC Investor Bulletin on Order Types: https://www.sec.gov/oiea/investor-alerts-and-bulletins/ib_ordertypes
