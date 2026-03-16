---
id: "trading/data-vendors/yfinance/gotchas"
title: "yfinance Gotchas and Silent Failures"
domain: "trading"
version: "1.0.0"
category: "data-vendors"
tags:
  - yfinance
  - adjusted-close
  - stock-splits
  - data-quality
severity: "CRITICAL"
last_verified: "2026-03-01"
applies_to:
  - python-agents
  - backtesting-systems
  - data-pipelines
related:
  - "trading/corporate-actions/stock-splits/handling"
---

# yfinance Gotchas and Silent Failures

## Summary

yfinance is the most common free data source for stock prices in Python, but it has multiple silent failure modes and breaking API changes that can corrupt backtests, produce wrong signals, or cause agents to trade on stale/incorrect data. These issues are especially dangerous because yfinance rarely raises exceptions — it prefers to return empty or subtly wrong data.

## The Problem

An agent that naively calls `yf.download("AAPL", start="2020-01-01")` may receive adjusted historical prices that differ from what the same call returned last month (due to subsequent dividends or splits). Column names may silently change between library versions, breaking downstream code. Invalid tickers return empty DataFrames instead of errors, so the agent proceeds with no data and no warning.

## Rules

1. **Adjusted close is the default and it changes retroactively.** yfinance returns split- and dividend-adjusted prices by default. After AAPL's 4:1 split on 2020-08-31, all pre-split close prices were divided by 4. After any dividend, all historical prices shift slightly. If your agent stores historical data, it will mismatch fresh downloads.

2. **Always specify `auto_adjust` explicitly.** As of yfinance v0.2.31+, the `auto_adjust` parameter defaults to `True`, meaning the `Close` column IS the adjusted close. In older versions, you got both `Close` (unadjusted) and `Adj Close` (adjusted). Do not assume which version is installed.

3. **Column names changed across versions.** Before v0.2.31: columns were `Open, High, Low, Close, Adj Close, Volume`. In v0.2.31+: `Adj Close` became `Adj_Close` (underscore). In some versions with `auto_adjust=True`, the `Adj Close`/`Adj_Close` column is dropped entirely. Always check `df.columns` before accessing by name.

4. **Invalid tickers return empty DataFrames — no exception raised.** `yf.download("INVALIDTICKER123")` returns an empty DataFrame. Your agent MUST check `df.empty` after every download call.

5. **Weekend and holiday queries return empty data silently.** Requesting data for a date range that falls entirely on weekends or holidays returns an empty DataFrame without any warning or error.

6. **Rate limiting and IP bans are real.** Yahoo Finance will throttle or ban IPs that make too many requests. There is no official rate limit documented. In practice, more than 2000 requests per hour from a single IP risks a temporary ban. Bans manifest as HTTP 429 errors or empty responses.

7. **Multi-ticker downloads can silently drop tickers.** `yf.download(["AAPL", "INVALIDTK"])` returns a MultiIndex DataFrame with data only for AAPL. The invalid ticker is silently omitted — no error, no warning in the DataFrame itself.

8. **Intraday data is limited to the last 60 days.** Requesting 1m or 5m interval data beyond 60 days returns empty results. The maximum lookback for 1h interval is ~730 days.

## Examples

### Adjusted price retroactive change
```python
# Downloaded on 2024-01-15:
# AAPL 2020-08-28 Close: $124.82 (post-split adjusted)
#
# Downloaded on 2024-07-15 (after more dividends):
# AAPL 2020-08-28 Close: $124.56 (different due to dividend adjustment)
#
# These are BOTH "correct" — they reflect adjustments known at download time.
```

### Silent failure on invalid ticker
```python
import yfinance as yf

df = yf.download("NOTREAL", start="2024-01-01", end="2024-01-31")
print(len(df))  # 0 — no error raised
print(df.empty)  # True — agent MUST check this

# Safe pattern:
df = yf.download("AAPL", start="2024-01-01", end="2024-01-31")
if df.empty:
    raise ValueError("No data returned for AAPL — check ticker and date range")
```

### Column name version differences
```python
# yfinance < 0.2.31
df.columns  # ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# yfinance >= 0.2.31 with auto_adjust=False
df.columns  # ['Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume']

# yfinance >= 0.2.31 with auto_adjust=True (default)
df.columns  # ['Open', 'High', 'Low', 'Close', 'Volume']
# 'Close' here IS the adjusted close. No separate column.

# Safe pattern — normalize columns:
adj_col = [c for c in df.columns if 'adj' in c.lower()]
close_price = df[adj_col[0]] if adj_col else df['Close']
```

### Rate limit mitigation
```python
import time
import yfinance as yf

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]  # etc.
# Download in batches, not one-by-one
df = yf.download(tickers, start="2024-01-01", group_by="ticker")
# Add delay between batch calls if doing multiple date ranges
time.sleep(1)
```

## Agent Checklist

- [ ] Check `df.empty` after every `yf.download()` call
- [ ] Explicitly set `auto_adjust=True` or `auto_adjust=False` — never rely on the default
- [ ] Do not hardcode column names like `Adj Close` — detect dynamically
- [ ] If storing historical data, record the download timestamp and yfinance version
- [ ] Implement rate limiting: batch tickers, add delays between calls
- [ ] Validate returned date range matches requested range
- [ ] For multi-ticker downloads, verify all requested tickers are present in the result
- [ ] Never use yfinance for intraday data older than 60 days

## Sources

- yfinance GitHub repository: https://github.com/ranaroussi/yfinance
- yfinance v0.2.31 changelog: https://github.com/ranaroussi/yfinance/releases/tag/0.2.31
- Yahoo Finance Terms of Service (unofficial API — no SLA)
- AAPL 4:1 stock split record date: 2020-08-24, effective: 2020-08-31
