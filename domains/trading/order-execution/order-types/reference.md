---
id: "trading/order-execution/order-types/reference"
title: "Order Types Reference"
domain: "trading"
version: "1.0.0"
category: "order-execution"
tags:
  - order-types
  - market-order
  - limit-order
  - stop-order
  - stop-limit
  - trailing-stop
  - bracket
  - oco
  - time-in-force
severity: "MEDIUM"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - order-execution-engines
  - portfolio-management-systems
related:
  - "trading/order-execution/best-execution/gotchas"
  - "trading/broker-apis/alpaca/quirks"
  - "trading/market-structure/trading-hours/reference"
---

# Order Types Reference

## Summary

Agents placing orders must understand the full spectrum of order types, their behaviors, and their risks. Using the wrong order type leads to poor fills (market orders in illiquid stocks), missed entries (limit orders set too aggressively), or unexpected losses (stop orders gapping through the trigger price). This reference covers all standard order types, their time-in-force options, and common rejection reasons.

## The Problem

An agent that only uses market orders will experience slippage in low-liquidity securities, pay wider spreads during extended hours, and have no price protection during volatile moves. An agent that only uses limit orders will miss fast-moving entries and exits. Stop orders become market orders after triggering and can fill far from the stop price during gaps. Each order type has specific behaviors that the agent must understand to select the right one for the situation.

## Rules

### Basic Order Types

1. **Market order.** Executes immediately at the best available price. Guarantees fill, does NOT guarantee price. Slippage risk in low-liquidity or volatile markets. Use for: highly liquid securities when immediate execution matters more than price.

2. **Limit order.** Executes only at the specified price or better. Buy limit: at or below the limit price. Sell limit: at or above the limit price. Guarantees price, does NOT guarantee fill. Use for: price-sensitive entries/exits, illiquid securities, or extended hours (required).

3. **Stop order (stop-loss).** Becomes a market order when the stop price is reached. Buy stop: triggers when price rises to the stop. Sell stop: triggers when price falls to the stop. Risk: gap through the stop price results in fill far from expected. Use for: protecting against large losses, but be aware of gap risk.

4. **Stop-limit order.** Becomes a limit order when the stop price is reached. Has two prices: stop price (trigger) and limit price (worst acceptable fill). Protects against gap-through, but may NOT fill if the price gaps past the limit. Use for: stop-loss with price protection in volatile stocks.

5. **Trailing stop.** A stop order that follows the price by a fixed amount or percentage. Buy trailing stop: trails below the rising price. Sell trailing stop: trails above the falling price. Adjusts automatically as the price moves favorably. Use for: locking in profits while allowing upside. Note: trailing stop reset behavior varies by broker — some reset the trail on every new high/low tick, others only reset on a new high/low close. Verify broker-specific behavior before relying on this order type.

### Advanced Order Types

6. **Bracket order.** Three linked orders: entry order + take-profit limit + stop-loss. The entry order must fill before the exit orders become active — they are not live until the entry is confirmed filled. When one exit fills, the other is automatically cancelled. Use for: fully automated trade management with predefined risk/reward.

7. **OCO (one-cancels-other).** Two orders linked together. When one fills, the other is automatically cancelled. Common use: place a limit sell above current price (take profit) and a stop sell below (stop loss). Use for: setting both upside and downside exits simultaneously.

### Time-in-Force Options

8. **DAY.** Order expires at market close if not filled. Default for most order types. Cancelled automatically at 4:00 PM ET (or end of extended hours session if enabled).

9. **GTC (good till cancel).** Order remains active until filled or manually cancelled. Most brokers auto-cancel after 60-90 days. Use for: patient limit orders at specific price targets.

10. **IOC (immediate or cancel).** Must fill immediately (in whole or part). Any unfilled portion is cancelled. Use for: large orders where partial fill is acceptable but waiting is not.

11. **FOK (fill or kill).** Must fill the ENTIRE quantity immediately or the entire order is cancelled. No partial fills. Use for: orders where partial fill is not acceptable (e.g. pairs trades).

12. **GTD (good till date).** Order remains active until a specified date. Less common, not supported by all brokers.

### Extended Hours and Special Considerations

13. **Extended hours restriction.** Only limit orders are allowed during pre-market (4:00-9:30 AM ET) and after-hours sessions. Market orders, stop orders, and other types are rejected. After-hours end times differ by exchange: NYSE after-hours runs until 8:00 PM ET; NASDAQ extended hours may vary by broker (some allow trading until 8:00 PM ET, others cut off at 6:00 PM ET). Check broker-specific extended hours windows.

14. **Odd lot vs round lot.** Orders for less than 100 shares (odd lots) may have lower execution priority on some exchanges. Fractional share orders are typically executed by the broker internally, not on the exchange.

15. **Common rejection reasons.** Insufficient buying power, stock is halted, PDT restriction active, order price too far from current market, extended hours with non-limit order type, account restricted (GFV or other violation), order size exceeds exchange maximum (typically 25,000 shares for NYSE), security on restricted list (IPO lock-up, regulatory halt, broker-specific restrictions).

## Examples

### Order type selection logic
```python
def select_order_type(
    side: str,
    urgency: str,
    liquidity: str,
    extended_hours: bool,
) -> str:
    """Select appropriate order type based on conditions."""
    if extended_hours:
        return "limit"  # Only limit orders allowed

    if urgency == "immediate" and liquidity == "high":
        return "market"

    if urgency == "immediate" and liquidity == "low":
        return "limit"  # Avoid slippage in illiquid stocks

    if urgency == "patient":
        return "limit"

    return "limit"  # Default to limit for safety
```

### Bracket order setup
```python
def create_bracket_order(
    symbol: str,
    entry_price: float,
    take_profit_pct: float = 0.03,  # 3% profit target
    stop_loss_pct: float = 0.02,    # 2% stop loss
) -> dict:
    """Create a bracket order with take-profit and stop-loss."""
    return {
        "entry": {"type": "limit", "price": entry_price, "side": "buy"},
        "take_profit": {
            "type": "limit",
            "price": round(entry_price * (1 + take_profit_pct), 2),
            "side": "sell",
        },
        "stop_loss": {
            "type": "stop",
            "price": round(entry_price * (1 - stop_loss_pct), 2),
            "side": "sell",
        },
    }
```

### Time-in-force quick reference
```
| TIF | Fill Guarantee | Duration        | Partial Fill |
|-----|---------------|-----------------|--------------|
| DAY | No            | Until close     | Yes          |
| GTC | No            | 60-90 days      | Yes          |
| IOC | No            | Immediate       | Yes          |
| FOK | No            | Immediate       | No           |
```

## Agent Checklist

- [ ] Use limit orders for illiquid securities (< 100k daily volume)
- [ ] Use limit orders during extended hours (market orders rejected)
- [ ] Set stop-losses with limit prices to avoid gap-through fills
- [ ] Check if broker supports bracket/OCO orders before using
- [ ] Verify time-in-force is appropriate (don't leave stale GTC orders)
- [ ] Monitor for partial fills on IOC/FOK orders
- [ ] Handle order rejections gracefully with retry logic
- [ ] Log all order submissions with type, price, TIF for audit trail

## Structured Checks

```yaml
checks:
  - id: order_type_extended_hours
    condition: "extended_hours != 'true' OR order_type == 'limit'"
    severity: high
    message: "Only limit orders allowed during extended hours"
```

## Sources

- SEC Investor Bulletin: Understanding Order Types
- FINRA: Types of Orders
- NYSE Order Type Reference
- CBOE Order Type Specifications
- Alpaca API: Order Types Documentation
