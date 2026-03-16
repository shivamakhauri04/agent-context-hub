---
id: "trading/broker-apis/alpaca/quirks"
title: "Alpaca Broker API Quirks"
domain: "trading"
version: "1.0.0"
category: "broker-apis"
tags:
  - alpaca
  - broker-api
  - paper-trading
  - order-types
severity: "HIGH"
last_verified: "2026-03-01"
applies_to:
  - trading-agents
  - order-execution-engines
  - paper-trading-systems
related:
  - "trading/regulations/pdt-rule/rules"
  - "trading/market-structure/trading-hours/reference"
---

# Alpaca Broker API Quirks

## Summary

Alpaca is one of the most popular brokers for algorithmic trading due to its commission-free trades and well-documented API. However, there are significant behavioral differences between paper and live trading, subtle order state machine quirks, restrictions on extended-hours trading, and PDT enforcement even in paper mode. Agents that work perfectly in paper trading often fail in production due to these differences.

## The Problem

An agent developed and tested entirely in paper trading will encounter different fill behavior, timing, and rejection patterns when switched to live trading. Paper trading simulates fills at the quoted price, ignoring slippage, partial fills, and real market impact. Agents that hardcode market hours instead of using the Clock API break during holidays and half days. The order state machine has intermediate states that agents rarely handle, causing orders to get stuck or be double-submitted.

## Rules

1. **Paper and live trading use different base URLs.** Paper: `https://paper-api.alpaca.markets`. Live: `https://api.alpaca.markets`. Using the wrong URL is the most common deployment mistake. The API key determines which environment it belongs to — a paper key will not authenticate against the live URL and vice versa.

2. **Paper trading fills are unrealistic.** Paper trading simulates fills using the NBBO (National Best Bid and Offer) at the time the order is processed. This means:
   - Market orders fill at the current quoted price with zero slippage
   - Limit orders fill if the price crosses the limit, regardless of volume
   - Large orders that would move the market in real life fill completely at quoted price
   - Fill latency is near-zero vs. real latency of 10-100ms in production

   Agents tested only in paper mode will overestimate strategy performance.

3. **Fractional shares are supported but not for all order types.** Fractional shares (e.g., buy 0.5 shares of AMZN) work with market and limit orders only. Fractional shares are NOT supported for stop orders, stop-limit orders, or trailing stop orders. Submitting a fractional stop order results in a rejection.

4. **Order state machine has intermediate states.** The full order lifecycle is:
   ```
   new -> accepted -> (pending_new) -> partially_filled -> filled
                   -> (pending_cancel) -> canceled
                   -> rejected
                   -> expired
   ```
   The `pending_new` and `pending_cancel` states are transient but real. An agent that only checks for `filled` or `canceled` may miss orders stuck in `pending_new` (which can last seconds to minutes during high-load periods). Always handle ALL states.

5. **Market orders during extended hours are REJECTED by default.** To place orders during pre-market or after-hours, you must explicitly set `extended_hours=True` AND use a limit order. Market orders are never accepted during extended hours. This is a common cause of rejected orders for agents that run before 9:30 AM ET.

6. **Use the Clock endpoint for market hours — never hardcode.** The `/v2/clock` endpoint returns the current market time, whether the market is open, and the next open/close times. Hardcoding "9:30 AM to 4:00 PM ET" breaks on:
   - Half days (1:00 PM close)
   - Market holidays
   - Emergency closures (rare but real, e.g., Hurricane Sandy 2012)

7. **PDT rule is enforced in paper trading.** Even with fake money, Alpaca enforces the Pattern Day Trader rule in paper accounts. If paper account equity is below $25,000 and you make 4+ day trades in 5 business days, the account is restricted. This catches many developers off guard during testing.

8. **Account equity includes unsettled funds differently.** `buying_power` and `equity` are different fields. `buying_power` for a margin account is typically 4x day-trade buying power during market hours and 2x overnight. For cash accounts, `buying_power` equals settled cash only. Always use `buying_power` (not `equity`) to determine if you can place an order.

9. **WebSocket streaming has separate endpoints for data and trade updates.** Market data streams from `wss://stream.data.alpaca.markets/v2/{source}` (source = `iex` or `sip`). Trade/account updates stream from `wss://paper-api.alpaca.markets/stream` (paper) or `wss://api.alpaca.markets/stream` (live). Connecting to the wrong stream is a common mistake.

10. **Order replacement (PATCH) can silently fail.** When you try to replace an order that is already partially filled, the replacement may be rejected. Always check the response and handle the case where the original order continues to fill during the replacement attempt.

## Examples

### Correct environment detection
```python
import os

ALPACA_ENV = os.getenv("ALPACA_ENV", "paper")

BASE_URL = {
    "paper": "https://paper-api.alpaca.markets",
    "live": "https://api.alpaca.markets",
}[ALPACA_ENV]

# CRITICAL: Log which environment we're using on every startup
print(f"Alpaca environment: {ALPACA_ENV} -> {BASE_URL}")
```

### Using the Clock endpoint
```python
import requests

def is_market_open(base_url: str, headers: dict) -> dict:
    resp = requests.get(f"{base_url}/v2/clock", headers=headers)
    clock = resp.json()
    return {
        "is_open": clock["is_open"],
        "next_open": clock["next_open"],
        "next_close": clock["next_close"],
        "timestamp": clock["timestamp"],
    }

# WRONG:
from datetime import datetime
import pytz
et = pytz.timezone("US/Eastern")
now_et = datetime.now(et)
is_open = now_et.hour >= 9 and (now_et.hour > 9 or now_et.minute >= 30) and now_et.hour < 16
# Breaks on holidays, half days, emergency closures

# RIGHT:
clock = is_market_open(BASE_URL, headers)
if clock["is_open"]:
    execute_strategy()
```

### Handling all order states
```python
def handle_order_update(order: dict):
    status = order["status"]

    if status == "new":
        log("Order submitted, awaiting acceptance")
    elif status == "accepted":
        log("Order accepted by exchange")
    elif status == "pending_new":
        log("Order in intermediate state — do NOT resubmit")
    elif status == "partially_filled":
        filled = int(order["filled_qty"])
        total = int(order["qty"])
        log(f"Partially filled: {filled}/{total}")
    elif status == "filled":
        log(f"Order fully filled at avg price {order['filled_avg_price']}")
    elif status == "pending_cancel":
        log("Cancel requested — not yet confirmed. Do NOT assume canceled.")
    elif status == "canceled":
        log("Order canceled")
    elif status == "rejected":
        log(f"Order REJECTED: check buying power, PDT, extended hours settings")
    elif status == "expired":
        log("Order expired (e.g., day order after market close)")
    else:
        log(f"Unknown order status: {status}")
```

### Extended hours limit order
```python
def place_extended_hours_order(api, ticker, qty, limit_price):
    """Place an order during pre-market or after-hours."""
    # Market orders are ALWAYS rejected during extended hours
    order = api.submit_order(
        symbol=ticker,
        qty=qty,
        side="buy",
        type="limit",           # MUST be limit, not market
        time_in_force="day",
        limit_price=limit_price,
        extended_hours=True,    # MUST be explicitly set
    )
    return order
```

## Agent Checklist

- [ ] Verify the base URL matches the intended environment (paper vs live) on every startup
- [ ] Log the environment clearly at startup to prevent accidental live trading
- [ ] Use the `/v2/clock` endpoint to check market hours — never hardcode hours or holidays
- [ ] Handle ALL order states including `pending_new`, `pending_cancel`, and `expired`
- [ ] Use limit orders with `extended_hours=True` for pre-market and after-hours trading
- [ ] Check `buying_power` (not `equity`) before placing orders
- [ ] Implement slippage assumptions for backtesting — paper fills are unrealistically good
- [ ] Track PDT count even in paper trading
- [ ] Use fractional shares only with market and limit orders
- [ ] Separate data WebSocket and trade update WebSocket connections
- [ ] Handle order replacement failures gracefully (check for partial fills before replacing)

## Sources

- Alpaca API Documentation: https://docs.alpaca.markets
- Alpaca Trading API Reference: https://docs.alpaca.markets/reference
- Alpaca Paper Trading Guide: https://docs.alpaca.markets/docs/paper-trading
- Alpaca Order Lifecycle: https://docs.alpaca.markets/docs/orders-at-alpaca
- Alpaca Extended Hours Trading: https://docs.alpaca.markets/docs/extended-hours
