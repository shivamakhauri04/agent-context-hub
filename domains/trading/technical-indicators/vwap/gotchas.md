---
id: "trading/technical-indicators/vwap/gotchas"
title: "VWAP Calculation Gotchas"
domain: "trading"
version: "1.0.0"
category: "technical-indicators"
tags:
  - vwap
  - technical-analysis
  - intraday
  - volume
severity: "HIGH"
last_verified: "2026-03-01"
applies_to:
  - trading-agents
  - technical-analysis-systems
  - backtesting-systems
related:
  - "trading/market-structure/trading-hours/reference"
  - "trading/data-vendors/yfinance/gotchas"
---

# VWAP Calculation Gotchas

## Summary

Volume Weighted Average Price (VWAP) is one of the most widely used institutional benchmarks, but it is also one of the most commonly miscalculated indicators by trading agents. VWAP resets daily and requires intraday data — computing it on daily bars is meaningless. Pre/post-market data skews VWAP due to low volume, and anchored VWAP has entirely different semantics from standard VWAP. An agent that misuses VWAP will generate systematically wrong trading signals.

## The Problem

VWAP is deceptively simple: `cumulative(price * volume) / cumulative(volume)`. But the "cumulative" part resets at the start of each regular trading session. Agents frequently make these mistakes: (1) computing VWAP on daily OHLCV bars, which produces a multi-day moving average that is not VWAP, (2) not resetting at market open, causing yesterday's volume to distort today's indicator, (3) including pre-market prints that skew the calculation with low-volume outlier prices, and (4) using VWAP in after-hours when it has no institutional relevance.

## Rules

1. **VWAP resets every trading day at market open (9:30 AM ET).** The cumulative sum of `price * volume` and cumulative sum of `volume` both reset to zero at 9:30 AM ET each day. VWAP from yesterday has NO relevance to today. An agent must never carry VWAP state across overnight gaps.

2. **VWAP requires intraday bar data.** The formula uses the typical price of each intraday bar:
   ```
   typical_price = (high + low + close) / 3
   VWAP = cumsum(typical_price * volume) / cumsum(volume)
   ```
   Computing this on daily bars gives you a volume-weighted average of daily typical prices over multiple days — this is a completely different (and largely useless) indicator. Use 1-minute or 5-minute bars at minimum.

3. **Pre-market VWAP is unreliable.** Pre-market (4:00-9:30 AM ET) has very low volume. A single large print at an extreme price can move VWAP significantly. Most institutional traders consider VWAP valid only from 9:30 AM onward. If your agent includes pre-market data in VWAP, it should be a deliberate and documented choice.

4. **Post-market VWAP is unreliable for the same reason.** After 4:00 PM ET, volume drops drastically. VWAP continues to update but becomes increasingly unreliable as thin volume allows individual trades to disproportionately affect the calculation. Do not use VWAP as a trading signal during after-hours.

5. **Never use closing auction data in intraday VWAP.** The NYSE closing auction (at exactly 4:00 PM) often produces a massive volume spike at a single price. Including this in a VWAP that was being tracked throughout the day creates a discontinuity. The closing auction VWAP print is a separate benchmark (the "closing VWAP") and should not be mixed with intraday running VWAP.

6. **Anchored VWAP is a different indicator.** Standard VWAP resets daily. Anchored VWAP (AVWAP) starts from a user-specified point — an earnings date, a swing low, a gap up, etc. It does NOT reset daily. AVWAP is useful for multi-day analysis but is not a substitute for standard VWAP and should not be labeled as "VWAP."

7. **VWAP is a lagging indicator that becomes stale.** Early in the session (9:30-10:00 AM), VWAP responds quickly to price/volume changes. By 3:00 PM, the cumulative denominator is so large that new bars barely move VWAP. This is by design — VWAP represents the average price of ALL volume for the day. But agents should not expect VWAP to be a responsive signal in the afternoon.

8. **VWAP bands (standard deviation bands) require careful calculation.** VWAP bands add +/- N standard deviations from VWAP. The standard deviation must be calculated as the volume-weighted variance of typical prices from VWAP, not the standard deviation of prices alone.

## Examples

### Correct intraday VWAP calculation
```python
import pandas as pd

def compute_vwap(bars: pd.DataFrame) -> pd.Series:
    """
    Compute VWAP from intraday bars.

    Args:
        bars: DataFrame with columns 'high', 'low', 'close', 'volume'
              Index should be a DatetimeIndex with intraday timestamps.
              Must be single-day data or grouped by date first.
    """
    typical_price = (bars['high'] + bars['low'] + bars['close']) / 3
    cum_tp_vol = (typical_price * bars['volume']).cumsum()
    cum_vol = bars['volume'].cumsum()
    vwap = cum_tp_vol / cum_vol
    return vwap

# CORRECT: Use 1-minute bars for a single day
bars_1m = get_intraday_bars("AAPL", interval="1m", date="2025-03-14")
vwap = compute_vwap(bars_1m)

# WRONG: Using daily bars
daily_bars = get_daily_bars("AAPL", start="2025-01-01", end="2025-03-14")
fake_vwap = compute_vwap(daily_bars)  # This is NOT VWAP!
```

### Daily VWAP reset
```python
def compute_vwap_multi_day(bars: pd.DataFrame) -> pd.Series:
    """Compute VWAP with proper daily reset."""
    bars = bars.copy()
    bars['date'] = bars.index.date

    typical_price = (bars['high'] + bars['low'] + bars['close']) / 3
    bars['tp_vol'] = typical_price * bars['volume']

    # Group by date to reset cumulative sums daily
    bars['cum_tp_vol'] = bars.groupby('date')['tp_vol'].cumsum()
    bars['cum_vol'] = bars.groupby('date')['volume'].cumsum()

    vwap = bars['cum_tp_vol'] / bars['cum_vol']
    return vwap
```

### Filtering pre-market data
```python
from datetime import time

def compute_rth_vwap(bars: pd.DataFrame) -> pd.Series:
    """Compute VWAP using Regular Trading Hours only (9:30 AM - 4:00 PM ET)."""
    # Filter to regular trading hours only
    rth_start = time(9, 30)
    rth_end = time(16, 0)

    # Assuming bars.index is in US/Eastern timezone
    rth_bars = bars.between_time(rth_start, rth_end)

    if rth_bars.empty:
        return pd.Series(dtype=float)

    return compute_vwap(rth_bars)
```

### VWAP with standard deviation bands
```python
def compute_vwap_bands(bars: pd.DataFrame, num_std: float = 2.0):
    """Compute VWAP with upper and lower bands."""
    typical_price = (bars['high'] + bars['low'] + bars['close']) / 3

    cum_tp_vol = (typical_price * bars['volume']).cumsum()
    cum_vol = bars['volume'].cumsum()
    vwap = cum_tp_vol / cum_vol

    # Volume-weighted variance
    cum_tp2_vol = (typical_price ** 2 * bars['volume']).cumsum()
    variance = (cum_tp2_vol / cum_vol) - vwap ** 2
    std = variance.clip(lower=0).pow(0.5)  # clip to avoid sqrt of negative

    return {
        'vwap': vwap,
        'upper_band': vwap + num_std * std,
        'lower_band': vwap - num_std * std,
    }
```

### Anchored VWAP (different from standard VWAP)
```python
def compute_anchored_vwap(bars: pd.DataFrame, anchor_date: str) -> pd.Series:
    """
    Anchored VWAP: starts from a specific date and does NOT reset daily.
    Used for multi-day analysis from a significant event (earnings, gap, etc.)

    This is NOT the same as standard VWAP. Do not confuse the two.
    """
    # Filter bars from anchor date onward
    anchor_bars = bars[bars.index >= anchor_date]

    typical_price = (anchor_bars['high'] + anchor_bars['low'] + anchor_bars['close']) / 3
    cum_tp_vol = (typical_price * anchor_bars['volume']).cumsum()
    cum_vol = anchor_bars['volume'].cumsum()

    return cum_tp_vol / cum_vol

# Example: AVWAP from AAPL's last earnings date
avwap = compute_anchored_vwap(aapl_1m_bars, anchor_date="2025-01-30")
```

## Agent Checklist

- [ ] Verify you are using intraday bars (1m, 5m, 15m), NEVER daily bars for VWAP
- [ ] Reset VWAP calculation at 9:30 AM ET each trading day
- [ ] Decide explicitly whether to include pre-market data (default: exclude)
- [ ] Do not use VWAP signals during after-hours or pre-market
- [ ] Handle the closing auction volume spike separately from intraday VWAP
- [ ] If using VWAP bands, compute volume-weighted variance (not simple variance)
- [ ] Distinguish standard VWAP from anchored VWAP in code and naming
- [ ] Account for VWAP's increasing staleness as the trading day progresses
- [ ] Ensure timezone handling is correct (VWAP resets at 9:30 AM ET, not UTC)
- [ ] If fetching VWAP from an API, verify whether it includes pre-market data or not

## Structured Checks

```yaml
checks:
  - id: vwap_intraday_only
    condition: "bar_interval != 'daily'"
    severity: critical
    message: "VWAP requires intraday bars — daily bars produce meaningless values"
  - id: vwap_session_reset
    condition: "cumulative_reset_at_open == 'true'"
    severity: high
    message: "VWAP cumulative sums must reset at market open (9:30 AM ET)"
```

## Sources

- CFA Institute, "Volume-Weighted Average Price (VWAP)"
- NYSE TAQ (Trades and Quotes) Data Specifications
- Berkowitz, Logue, Noser (1988), "The Total Cost of Transactions on the NYSE" (foundational VWAP paper)
- Alpaca VWAP documentation: https://docs.alpaca.markets/docs/vwap
