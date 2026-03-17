---
id: "trading/market-structure/trading-hours/reference"
title: "US Equity Market Trading Hours and Holidays"
domain: "trading"
version: "1.0.0"
category: "market-structure"
tags:
  - market-hours
  - nyse
  - nasdaq
  - holidays
  - extended-hours
severity: "MEDIUM"
last_verified: "2026-03-01"
applies_to:
  - trading-agents
  - order-scheduling-systems
  - data-pipelines
related:
  - "trading/broker-apis/alpaca/quirks"
  - "trading/technical-indicators/vwap/gotchas"
---

# US Equity Market Trading Hours and Holidays

## Summary

US equity markets (NYSE, NASDAQ) follow a well-defined schedule of regular hours, extended hours, holidays, and early-close days. Trading agents must reference this schedule to avoid submitting orders when markets are closed, computing indicators on non-trading periods, and missing early-close days that differ from the normal 4:00 PM close. Hardcoding market hours is a common source of agent failures — always query the broker's clock API when possible.

## The Problem

An agent that hardcodes "market is open 9:30 AM to 4:00 PM ET, Monday through Friday" will fail on 9 full holidays, 3 half days, and any emergency closure. On half days, the market closes at 1:00 PM ET, and an agent that places orders at 2:00 PM will have them rejected. Agents that do not account for extended-hours sessions miss opportunities or submit orders that are rejected for lacking the `extended_hours` flag.

## Rules

1. **Regular Trading Hours (RTH): 9:30 AM - 4:00 PM Eastern Time.** This applies to both NYSE and NASDAQ. All order types are accepted. Maximum liquidity.

2. **Pre-market session: 4:00 AM - 9:30 AM ET.** Not all brokers support this full window. Some (like Alpaca) support only 7:00 AM - 9:30 AM for extended-hours orders. Only limit orders are accepted — market orders are rejected. Liquidity is thin, spreads are wider, and prices are more volatile.

3. **After-hours session: 4:00 PM - 8:00 PM ET.** Same constraints as pre-market: limit orders only, thin liquidity, wider spreads. Some brokers cut off at 6:00 PM or 7:00 PM. Earnings announcements after 4:00 PM can cause significant after-hours price moves.

4. **Early-close (half) days: market closes at 1:00 PM ET.** These occur 3 times per year:
   - Day before Independence Day (July 3, unless July 4 is a Saturday, then no early close; if July 4 is a Sunday, early close on July 2)
   - Day after Thanksgiving (Black Friday)
   - Christmas Eve (December 24, unless Christmas is on a weekend — see holiday rules below)

   On half days, there is typically no after-hours session.

5. **NYSE 2026 Full Holiday Schedule (market fully closed):**

   | Date | Holiday |
   |------|---------|
   | January 1, 2026 (Thursday) | New Year's Day |
   | January 19, 2026 (Monday) | Martin Luther King Jr. Day |
   | February 16, 2026 (Monday) | Presidents' Day |
   | April 3, 2026 (Friday) | Good Friday |
   | May 25, 2026 (Monday) | Memorial Day |
   | June 19, 2026 (Friday) | Juneteenth |
   | July 3, 2026 (Friday) | Independence Day (observed; July 4 is Saturday) |
   | September 7, 2026 (Monday) | Labor Day |
   | November 26, 2026 (Thursday) | Thanksgiving Day |
   | December 25, 2026 (Friday) | Christmas Day |

6. **NYSE 2026 Early-Close Days (1:00 PM ET close):**

   | Date | Reason |
   |------|--------|
   | July 2, 2026 (Thursday) | Day before Independence Day (observed) |
   | November 27, 2026 (Friday) | Day after Thanksgiving |
   | December 24, 2026 (Thursday) | Christmas Eve |

7. **Weekend/holiday rules.** If a holiday falls on Saturday, the market closes the preceding Friday. If a holiday falls on Sunday, the market closes the following Monday. Exception: if July 4 is on a Saturday, the early close is on Thursday July 2 (not Friday July 3, as Friday becomes the holiday observance).

8. **Liquidity differs significantly across sessions.** Approximate volume distribution for a typical stock:
   - Pre-market (4:00-9:30 AM): ~2-5% of daily volume
   - Opening auction (9:30 AM): ~5-10% of daily volume in the first 30 minutes
   - Midday (10:00 AM - 3:00 PM): ~40-50% of daily volume
   - Closing auction (3:30-4:00 PM): ~20-30% of daily volume
   - After-hours (4:00-8:00 PM): ~2-5% of daily volume

   Agents should expect significantly worse fills (wider spreads, more slippage) outside regular hours.

9. **Circuit breakers can halt trading intraday.** Market-wide circuit breakers (Level 1, 2, 3) halt trading when the S&P 500 drops by 7%, 13%, or 20% from the prior day's close:
   - Level 1 (7% drop): 15-minute halt (only triggers before 3:25 PM)
   - Level 2 (13% drop): 15-minute halt (only triggers before 3:25 PM)
   - Level 3 (20% drop): market closes for the rest of the day

   Individual stocks can also be halted via LULD (Limit Up-Limit Down) mechanism.

10. **Time zone matters.** All market hours are in US Eastern Time (ET). This is EST (UTC-5) in winter and EDT (UTC-4) in summer. Daylight saving transitions happen in March and November. An agent in UTC must adjust for this. Use `pytz` or `zoneinfo` — never manually add/subtract hours.

## Examples

### Market hours checker using zoneinfo
```python
from datetime import datetime, time
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

NYSE_HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
    "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-12-25",
}

NYSE_EARLY_CLOSE_2026 = {
    "2026-07-02", "2026-11-27", "2026-12-24",
}

RTH_OPEN = time(9, 30)
RTH_CLOSE = time(16, 0)
EARLY_CLOSE = time(13, 0)
PRE_MARKET_OPEN = time(4, 0)
AFTER_HOURS_CLOSE = time(20, 0)

def get_market_status(dt: datetime = None) -> dict:
    if dt is None:
        dt = datetime.now(ET)
    else:
        dt = dt.astimezone(ET)

    date_str = dt.strftime("%Y-%m-%d")
    t = dt.time()
    weekday = dt.weekday()  # 0=Mon, 6=Sun

    if weekday >= 5 or date_str in NYSE_HOLIDAYS_2026:
        return {"status": "closed", "reason": "weekend/holiday"}

    close_time = EARLY_CLOSE if date_str in NYSE_EARLY_CLOSE_2026 else RTH_CLOSE

    if RTH_OPEN <= t < close_time:
        return {"status": "open", "session": "regular", "closes_at": str(close_time)}
    elif PRE_MARKET_OPEN <= t < RTH_OPEN:
        return {"status": "open", "session": "pre-market", "rth_opens_at": str(RTH_OPEN)}
    elif close_time <= t < AFTER_HOURS_CLOSE and date_str not in NYSE_EARLY_CLOSE_2026:
        return {"status": "open", "session": "after-hours", "closes_at": str(AFTER_HOURS_CLOSE)}
    else:
        return {"status": "closed", "reason": "outside all sessions"}
```

### Using broker Clock API (preferred over hardcoding)
```python
# PREFERRED: Use Alpaca Clock API
import requests

def get_market_clock(base_url: str, api_key: str) -> dict:
    headers = {"APCA-API-KEY-ID": api_key}
    resp = requests.get(f"{base_url}/v2/clock", headers=headers)
    return resp.json()

clock = get_market_clock(BASE_URL, API_KEY)
# Returns:
# {
#   "timestamp": "2026-03-16T10:30:00-04:00",
#   "is_open": true,
#   "next_open": "2026-03-17T09:30:00-04:00",
#   "next_close": "2026-03-16T16:00:00-04:00"
# }
```

### Handling timezone correctly
```python
from zoneinfo import ZoneInfo
from datetime import datetime

# WRONG: manual offset
utc_now = datetime.utcnow()
et_hour = utc_now.hour - 5  # Breaks during daylight saving time!

# RIGHT: use timezone-aware datetimes
et = ZoneInfo("America/New_York")
now_et = datetime.now(et)
print(f"Current ET time: {now_et.strftime('%H:%M:%S %Z')}")
# Automatically handles EST/EDT transitions
```

### Liquidity-aware order sizing
```python
def adjust_for_session(order_qty: int, session: str) -> int:
    """Reduce order size in low-liquidity sessions to minimize market impact."""
    multipliers = {
        "pre-market": 0.25,     # 25% of intended size
        "regular": 1.0,         # Full size
        "after-hours": 0.25,    # 25% of intended size
        "opening-30min": 0.5,   # First 30 min can be volatile
        "closing-30min": 0.75,  # Closing auction adds liquidity
    }
    return max(1, int(order_qty * multipliers.get(session, 0.25)))
```

## Agent Checklist

- [ ] Use a broker Clock API (e.g., Alpaca `/v2/clock`) instead of hardcoding market hours
- [ ] Maintain a holiday calendar and update it annually (or query the broker calendar API)
- [ ] Handle early-close days (1:00 PM ET) — do not assume 4:00 PM close every day
- [ ] Use timezone-aware datetimes with `zoneinfo` or `pytz` — never manually offset UTC
- [ ] Account for daylight saving time transitions (March and November)
- [ ] Reduce order sizes and expect worse fills during pre-market and after-hours
- [ ] Use only limit orders during extended hours
- [ ] Handle market-wide circuit breakers and individual stock halts gracefully
- [ ] Do not schedule recurring tasks (like daily rebalancing) at exactly 4:00 PM — the market might close at 1:00 PM on half days
- [ ] Test agent behavior on holidays and weekends — ensure it does not crash or submit orders

## Structured Checks

```yaml
checks:
  - id: market_open_check
    condition: "is_market_open == 'true' OR order_type == 'limit'"
    severity: high
    message: "Market order submitted outside regular trading hours"
  - id: half_day_check
    condition: "is_half_day == 'false' OR current_hour < 13"
    severity: medium
    message: "Trading after 1:00 PM on half day — market is closed"
```

## Sources

- NYSE Holiday Calendar: https://www.nyse.com/markets/hours-calendars
- NASDAQ Holiday Calendar: https://www.nasdaq.com/market-activity/stock-market-holiday-schedule
- SEC Rule 613 (Consolidated Audit Trail): market session definitions
- NYSE Rule 7.35A: Market-Wide Circuit Breakers
- LULD Plan: https://www.luldplan.com
