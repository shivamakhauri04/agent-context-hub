---
id: "trading/regulations/options-trading/rules"
title: "Options Trading Rules and Approval Levels"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - options
  - finra
  - approval-levels
  - assignment
  - expiration
  - greeks
severity: "CRITICAL"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - order-execution-engines
related:
  - "trading/regulations/pdt-rule/rules"
  - "trading/regulations/margin-requirements/rules"
---

# Options Trading Rules and Approval Levels

## Summary

Options trading requires explicit broker approval at specific levels (1-5). Each level unlocks progressively riskier strategies. The OCC auto-exercises in-the-money options at expiration if they are $0.01 or more ITM, which can cause unexpected capital requirements. Naked calls carry unlimited theoretical loss. Agents must verify approval level before placing any options order and must handle expiration risk proactively.

## The Problem

Trading agents that attempt options strategies without verifying the account's approval level will have orders rejected or, worse, will build positions the account cannot support. Common failures: (1) placing a credit spread on a Level 1 account, (2) ignoring auto-exercise at expiration and having insufficient capital to take delivery, (3) not understanding that American-style options can be assigned at any time (not just at expiration), (4) underestimating naked call risk where max loss is theoretically unlimited.

## Rules

1. **Approval Levels.** Brokers assign options approval levels based on experience, net worth, and risk tolerance. The standard levels are:

   | Level | Strategies Allowed |
   |-------|--------------------|
   | 1 | Covered calls, protective puts (must own underlying) |
   | 2 | Long calls, long puts (buying options outright) |
   | 3 | Debit spreads, credit spreads, iron condors, butterflies |
   | 4 | Naked (uncovered) puts |
   | 5 | Naked (uncovered) calls — unlimited loss risk |

2. **Expiration and Auto-Exercise.** The OCC (Options Clearing Corporation) automatically exercises options that are $0.01 or more in-the-money at expiration. This means a long call holder will be required to purchase 100 shares per contract at the strike price. If the account lacks sufficient capital, the broker will liquidate the position — often at unfavorable prices. Agents MUST check capital requirements before allowing ITM options to reach expiration.

3. **Assignment Risk.** American-style equity options can be assigned at any time before expiration. Assignment risk is elevated the day before an ex-dividend date (holders of short calls may be assigned early so the buyer can capture the dividend). European-style options (e.g., index options like SPX) can only be exercised at expiration.

4. **Maximum Loss by Strategy.**

   | Strategy | Maximum Loss |
   |----------|-------------|
   | Long call / long put | Premium paid |
   | Covered call | Underlying price to $0 minus premium received |
   | Protective put | Premium paid (underlying protected at strike) |
   | Credit spread | Width of spread minus premium received |
   | Debit spread | Premium paid |
   | Iron condor | Width of wider spread minus net premium received |
   | Naked put | Strike price minus premium received (stock to $0) |
   | Naked call | **UNLIMITED** (stock can rise without bound) |

5. **The Greeks.** Options pricing is driven by five risk measures:
   - **Delta**: Rate of change in option price per $1 move in underlying. Calls: 0 to 1, Puts: -1 to 0.
   - **Gamma**: Rate of change in Delta. Highest for ATM options near expiration.
   - **Theta**: Time decay per day. Options lose value as expiration approaches (accelerates in final 30 days).
   - **Vega**: Sensitivity to implied volatility. Long options benefit from rising IV.
   - **Rho**: Sensitivity to interest rate changes. Generally small impact.

6. **Exercise Settlement.** Equity options settle T+1 (one business day after exercise) since the SEC shortened settlement in May 2024. Index options are typically cash-settled.

7. **Contract Multiplier.** Standard equity options represent 100 shares per contract. A $5.00 premium costs $500 per contract. Agents must multiply by 100 when calculating capital requirements.

8. **Options on Expiration Friday.** Many brokers restrict opening new positions on expiration day. Short options that are near-the-money on expiration day carry "pin risk" — the risk of uncertain assignment.

## Examples

### Approval level check before order
```python
STRATEGY_LEVELS = {
    "covered_call": 1, "protective_put": 1,
    "long_call": 2, "long_put": 2,
    "debit_spread": 3, "credit_spread": 3, "iron_condor": 3,
    "naked_put": 4,
    "naked_call": 5,
}

def can_trade_strategy(account_level: int, strategy: str) -> bool:
    required = STRATEGY_LEVELS.get(strategy)
    if required is None:
        return False  # Unknown strategy — reject
    return account_level >= required
```

### Expiration capital check
```python
def check_expiration_risk(options: list[dict], cash: float) -> list[str]:
    warnings = []
    for opt in options:
        if opt["days_to_expiration"] <= 1 and opt["moneyness"] == "ITM":
            exercise_cost = opt["strike"] * 100 * opt["contracts"]
            if exercise_cost > cash:
                warnings.append(
                    f"{opt['symbol']}: ITM at expiration, exercise cost "
                    f"${exercise_cost:,.0f} exceeds cash ${cash:,.0f}"
                )
    return warnings
```

### Naked call risk scenario
```
Agent sells 10 TSLA $300 calls naked at $5.00 premium.
Premium received: $5,000 (10 contracts x $5.00 x 100)
If TSLA rises to $500: Loss = (500 - 300) x 1000 = $200,000
If TSLA rises to $1,000: Loss = (1000 - 300) x 1000 = $700,000
Max loss: UNLIMITED — there is no ceiling on stock price.
```

## Agent Checklist

- [ ] Query account options approval level before any options order
- [ ] Map each strategy to its required approval level and reject if insufficient
- [ ] Monitor expiring ITM options and ensure sufficient capital for exercise
- [ ] Track assignment risk for short options, especially before ex-dividend dates
- [ ] Always multiply premiums and strikes by 100 (contract multiplier)
- [ ] Handle partial fills on multi-leg strategies (legs may fill independently)
- [ ] Log Greeks for risk monitoring (especially Delta and Theta)
- [ ] Never allow naked calls without Level 5 approval and explicit risk acknowledgment

## Structured Checks

```yaml
checks:
  - id: options_approval_level
    condition: "options_approval_level >= required_approval_level"
    severity: critical
    message: "Strategy requires higher options approval level than account has"
  - id: options_naked_call_check
    condition: "options_approval_level >= 5 OR has_naked_calls == 'false'"
    severity: critical
    message: "Naked calls require Level 5 approval — unlimited loss risk"
  - id: options_expiration_capital
    condition: "cash >= itm_exercise_cost OR days_to_expiration > 1"
    severity: critical
    message: "Insufficient capital for auto-exercise of ITM options at expiration"
```

## Sources

- OCC Auto-Exercise Rules: https://www.theocc.com/Clearance-and-Settlement/Clearing/Exercises-and-Assignments
- FINRA Options Regulation: https://www.finra.org/rules-guidance/key-topics/options
- CBOE Margin Manual: https://www.cboe.com/tradable_products/options/margin_manual/
- SEC T+1 Settlement (May 2024): https://www.sec.gov/rules/final/2023/34-96930.pdf
- FINRA Notice 24-09 (AI in Securities): https://www.finra.org/rules-guidance/notices/24-09
