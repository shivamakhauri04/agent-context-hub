---
id: "trading/data-vendors/polygon/gotchas"
title: "Polygon.io Gotchas and Integration Pitfalls"
domain: "trading"
version: "1.0.0"
category: "data-vendors"
tags:
  - polygon
  - real-time-data
  - websockets
  - rate-limits
severity: "HIGH"
last_verified: "2026-03-01"
applies_to:
  - python-agents
  - real-time-trading-systems
  - data-pipelines
related:
  - "trading/data-vendors/yfinance/gotchas"
  - "trading/market-structure/trading-hours/reference"
---

# Polygon.io Gotchas and Integration Pitfalls

## Summary

Polygon.io is a popular market data API offering REST and WebSocket endpoints for stocks, options, forex, and crypto. While more reliable than yfinance, it has tier-based limitations, silent WebSocket disconnections, and default behaviors around extended hours data that can catch agents off guard. Free-tier users face severe rate limits and delayed data that make real-time strategies impossible.

## The Problem

An agent on the free tier may believe it is receiving real-time data when it is actually 15 minutes delayed — leading to stale signals and bad fills. WebSocket connections drop without sending a close frame, so an agent that does not implement heartbeat/reconnection logic will silently stop receiving data. Aggregate bar endpoints exclude pre/post market data by default, which can cause overnight gap misinterpretation.

## Rules

1. **Free tier data is 15 minutes delayed.** The Polygon free plan ("Basic") provides end-of-day and 15-minute delayed data only. Real-time data requires the "Starter" plan ($29/mo) or higher. An agent MUST know which tier it is on and must never treat delayed data as real-time for order decisions.

2. **Free tier rate limit is 5 API calls per minute.** This is extremely restrictive. A single agent polling 10 tickers every minute will exceed this immediately. The Starter plan allows unlimited API calls. Implement exponential backoff and request batching on free tier.

3. **WebSocket connections drop silently.** Polygon WebSocket feeds can disconnect without sending a close frame, especially during high-volatility periods when you need data most. The agent MUST implement:
   - Heartbeat monitoring (expect a ping every ~30 seconds)
   - Automatic reconnection with exponential backoff
   - Sequence number tracking to detect missed messages
   - A maximum reconnection attempt limit to avoid infinite loops

4. **Aggregate bars exclude extended hours by default.** The `/v2/aggs/ticker/{ticker}/range/` endpoint returns regular-session bars only unless you explicitly set `adjusted=true` and use the `preMarket` and `afterHours` parameters (available on some plans). An agent analyzing overnight gaps must account for this.

5. **Historical data depth varies by plan.** Free tier: 2 years of historical data. Starter: 5 years. Developer and above: 10+ years. If your backtest requires 10 years of data and you are on the free tier, the API returns only the available portion without warning about truncation.

6. **Adjusted vs unadjusted data requires explicit parameter.** The `adjusted` query parameter defaults to `true` for aggregate endpoints. Like yfinance, this means historical prices change after splits and dividends. Be explicit about which you need.

7. **Ticker format differences for options and OTC.** Options tickers use the OCC format (e.g., `O:AAPL230120C00150000`). OTC stocks may have different ticker conventions. Using the wrong format returns empty results, not errors.

8. **Trades and quotes endpoints return massive volumes.** A single day of tick data for a liquid stock (AAPL, SPY) can be millions of records. Always use pagination (`limit` and `timestamp` cursor) and set reasonable `limit` values (max 50,000 per request).

## Examples

### Detecting plan tier and data delay
```python
import requests

# Check your plan's capabilities
resp = requests.get(
    "https://api.polygon.io/v1/meta/symbols/AAPL/company",
    params={"apiKey": API_KEY}
)
# If you get a 403 on real-time endpoints, you are on a delayed plan.

# WRONG: assuming real-time on free tier
last_trade = get_last_trade("AAPL")
# This price could be 15 minutes old on free tier!

# RIGHT: check the timestamp
from datetime import datetime, timezone, timedelta
trade_time = datetime.fromtimestamp(last_trade['t'] / 1e9, tz=timezone.utc)
now = datetime.now(timezone.utc)
delay = (now - trade_time).total_seconds()
if delay > 60:
    print(f"WARNING: data is {delay:.0f}s old — likely delayed tier")
```

### WebSocket reconnection pattern
```python
import asyncio
import websockets
import json

class PolygonWSClient:
    def __init__(self, api_key, tickers):
        self.api_key = api_key
        self.tickers = tickers
        self.ws_url = "wss://socket.polygon.io/stocks"
        self.max_retries = 10
        self.retry_count = 0

    async def connect(self):
        while self.retry_count < self.max_retries:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    self.retry_count = 0  # Reset on successful connect
                    await ws.send(json.dumps({"action": "auth", "params": self.api_key}))
                    await ws.send(json.dumps({
                        "action": "subscribe",
                        "params": ",".join(f"T.{t}" for t in self.tickers)
                    }))
                    async for message in ws:
                        await self.handle_message(json.loads(message))
            except websockets.ConnectionClosed:
                self.retry_count += 1
                wait = min(2 ** self.retry_count, 60)
                print(f"WS disconnected. Retry {self.retry_count}/{self.max_retries} in {wait}s")
                await asyncio.sleep(wait)
            except Exception as e:
                print(f"WS error: {e}")
                self.retry_count += 1
                await asyncio.sleep(5)
```

### Rate limit handling for free tier
```python
import time
from functools import wraps

def rate_limited(max_per_minute=5):
    """Decorator to enforce Polygon free-tier rate limits."""
    min_interval = 60.0 / max_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limited(max_per_minute=5)
def get_polygon_aggs(ticker, date):
    # Your API call here
    pass
```

## Agent Checklist

- [ ] Verify which Polygon plan tier the API key belongs to before making assumptions about data freshness
- [ ] Implement WebSocket reconnection with exponential backoff and max retry limit
- [ ] Track WebSocket message sequence numbers to detect gaps
- [ ] Set `adjusted` parameter explicitly on all aggregate endpoints
- [ ] Implement rate limiting appropriate to your plan tier (5/min for free)
- [ ] Use pagination for trades/quotes endpoints — never try to fetch a full day in one call
- [ ] Check response timestamps to verify data recency
- [ ] Handle 403 (forbidden) responses as plan-tier limitations, not transient errors
- [ ] Test with market-closed periods to ensure agent handles empty responses correctly

## Structured Checks

```yaml
checks:
  - id: polygon_rate_limit
    condition: "requests_per_minute <= 5 OR tier != 'free'"
    severity: high
    message: "Exceeding Polygon free tier rate limit (5 calls/minute)"
  - id: polygon_data_delay
    condition: "tier != 'free' OR accepts_delayed_data == 'true'"
    severity: medium
    message: "Polygon free tier data is delayed 15 minutes"
```

## Sources

- Polygon.io API documentation: https://polygon.io/docs
- Polygon.io pricing and plan comparison: https://polygon.io/pricing
- Polygon.io WebSocket documentation: https://polygon.io/docs/stocks/ws_getting-started
- Polygon.io rate limits FAQ: https://polygon.io/knowledge-base
