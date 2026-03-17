---
id: "trading/regulations/zero-dte-options/rules"
title: "Zero Days to Expiration (0DTE) Options"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - zero-dte
  - 0dte
  - options
  - gamma-risk
  - pin-risk
  - assignment
  - expiration
  - intraday
severity: "HIGH"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - options-trading-systems
  - risk-management-systems
related:
  - "trading/regulations/options-trading/rules"
  - "trading/regulations/margin-requirements/rules"
---

# Zero Days to Expiration (0DTE) Options

## Summary

0DTE options are options contracts that expire on the same trading day they are traded. They now represent over 40% of SPX options volume and are the fastest-growing segment of the options market. 0DTE positions carry unique risks: extreme gamma sensitivity, pin risk near the strike at close, auto-exercise of ITM options, and the possibility of total loss within hours. Agents trading 0DTE must enforce strict position sizing, understand exercise capital requirements, and handle the compressed time dynamics.

## The Problem

An agent that trades 0DTE options like regular options will be surprised by: (1) gamma explosion -- delta changes so rapidly near expiration that small underlying moves cause massive P&L swings, (2) pin risk -- when the underlying is near the strike at close, it's uncertain whether the option finishes ITM or OTM, leading to unexpected assignment, (3) auto-exercise creating stock positions far exceeding account equity, (4) inability to roll or adjust positions because time value has already decayed to near zero, and (5) total loss of premium within hours if the trade goes against you.

## Rules

1. **0DTE definition.** Options expiring on the same trading day. SPX has had daily expirations (Mon-Fri) since 2022; SPY since November 2023. For individual equity options, only Friday expirations were traditionally 0DTE, but many high-volume names now have Mon/Wed/Fri weeklies.

2. **Broker restrictions (check first).** Some brokers restrict 0DTE short selling for retail accounts or require higher options approval levels. Robinhood restricts selling 0DTE options entirely. TD Ameritrade/Schwab requires Level 3+ approval. Agents must verify broker permissions before any 0DTE strategy — this determines what strategies are even possible.

3. **Gamma risk.** As expiration approaches, gamma (rate of change of delta) increases dramatically for at-the-money options. A stock moving $1 can cause an ATM 0DTE option's delta to swing from 0.50 to 0.90, multiplying the position's directional exposure.

4. **Pin risk.** When the underlying price is near the strike at close, it's uncertain whether the option will finish in or out of the money. The option may be exercised or not based on after-hours price movement. OCC exercise cutoff: 5:30 PM ET for equity options, 4:30 PM ET for index options (SPX, NDX, RUT).

5. **Auto-exercise rule.** The OCC automatically exercises equity options that are $0.01 or more in-the-money at expiration. The holder can submit a do-not-exercise instruction, but must do so before the cutoff (5:30 PM ET equity, 4:30 PM ET index). Agents must handle this proactively.

6. **Assignment risk for sellers.** Short 0DTE options can be assigned at any point during the trading day via early exercise. For American-style equity options, the seller has no control over when assignment occurs.

7. **Exercise capital requirement.** Exercising or being assigned creates a stock position. One contract = 100 shares. If assigned on a short $500 strike put, the agent must buy 100 shares at $500 = $50,000. This can far exceed account equity.

8. **Position sizing.** Never risk more than a fixed percentage of portfolio equity on 0DTE positions. Common limits: 1-2% for conservative, up to 5% for aggressive. Total 0DTE exposure across all positions should be capped.

9. **AM vs PM settlement.** Index options (SPX, NDX, RUT) with AM settlement use the opening price on expiration morning for settlement. PM-settled options (most equity options, PM-settled SPX) use the closing price. Know which settlement applies.

10. **No overnight holding.** 0DTE positions expire worthless or are exercised by end of day. There is no opportunity to hold and wait for recovery. The agent must have an exit strategy before entering.

## Examples

### Gamma explosion scenario
```
SPX at 5200, 0DTE 5200 call at 10:00 AM:
  Price: $8.00, Delta: 0.50, Gamma: 0.08

SPX moves to 5205 (+5 points):
  New delta: 0.50 + (0.08 * 5) = 0.90
  Option price: ~$12.50 (up 56%)

SPX moves back to 5200:
  Delta drops back toward 0.50
  Option price: ~$6.00 (below original due to time decay)

SPX drops to 5195 instead (-5 points):
  New delta: 0.50 - (0.08 * 5) = 0.10
  Option price: ~$1.50 (down 81%)
  -> Near total loss on a $5 move against you.

The same $5 move at 10 AM vs 3 PM has vastly different gamma impact.
At 3 PM, gamma could be 0.20+, making the $5 move explosive.
```

### Position sizing
```python
def validate_zero_dte_position(
    max_loss: float,
    equity: float,
    max_portfolio_pct: float = 0.05,
) -> bool:
    """Validate 0DTE position is within risk limits."""
    if max_loss > equity * max_portfolio_pct:
        return False  # Exceeds portfolio allocation
    if max_loss > equity * 0.02:
        pass  # Warning: single position > 2% of equity
    return True

# Example: $100k equity, 5% max allocation = $5,000 total 0DTE risk
# Each position should be < $2,000 (2% per position)
```

### Exercise capital check
```
Short 1 SPX 5200 put (0DTE):
  Max assignment cost: 100 * $5,200 = $520,000
  Account equity: $50,000
  -> CRITICAL: Exercise cost 10x account equity

Short 1 AAPL 190 put (0DTE):
  Max assignment cost: 100 * $190 = $19,000
  Account equity: $50,000
  -> OK: Within account equity
```

## Agent Checklist

- [ ] Cap total 0DTE exposure to a fixed % of portfolio (e.g. 5%)
- [ ] Calculate exercise/assignment cost for every short position before entry
- [ ] Verify options approval level permits 0DTE short selling
- [ ] Set hard exit times (e.g. close all positions by 3:45 PM ET)
- [ ] Monitor gamma exposure in real-time -- it accelerates throughout the day
- [ ] Check for AM vs PM settlement on index options
- [ ] Never leave short 0DTE positions unmonitored near expiration
- [ ] Submit do-not-exercise instructions if holding ITM options you don't want exercised

## Structured Checks

```yaml
checks:
  - id: zero_dte_position_size
    condition: "zero_dte_total_risk == 0 OR zero_dte_total_risk <= equity * zero_dte_max_portfolio_pct"
    severity: high
    message: "0DTE position risk exceeds maximum portfolio allocation"
  - id: zero_dte_exercise_capital
    condition: "zero_dte_exercise_cost == 0 OR zero_dte_exercise_cost <= equity"
    severity: critical
    message: "0DTE option exercise cost exceeds account equity"
```

## Sources

- CBOE: 0DTE Options Overview
- OCC Exercise and Assignment Rules
- FINRA Options Guidance and 0DTE Risk Considerations
- SEC Investor Bulletin: Options Trading
- CBOE SPX Options Settlement Specifications
