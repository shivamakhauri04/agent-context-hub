---
id: "trading/regulations/event-contracts/rules"
title: "Event Contracts / Prediction Markets"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - event-contracts
  - prediction-markets
  - cftc
  - binary-options
  - kalshi
  - robinhood-predict
severity: "HIGH"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
related:
  - "trading/regulations/futures-trading/rules"
---

# Event Contracts / Prediction Markets

## Summary

Event contracts (prediction markets) are CFTC-regulated binary contracts that pay $0 or $1 based on the outcome of a real-world event. Platforms like Kalshi and Robinhood Predict offer these through designated contract markets (DCMs). These are NOT securities — they have no dividends, no corporate actions, no partial settlement. They are fully collateralized (no margin), have position limits, and their tax treatment is still evolving. Agents that treat event contracts like equities or options will miscalculate risk, taxes, and position sizing.

## The Problem

Agents encountering event contracts will make errors if they: (1) apply securities regulations (SEC/FINRA) instead of CFTC rules, (2) try to calculate Greeks or apply options pricing models (event contracts are binary, not continuous), (3) assume margin is available (event contracts must be fully collateralized), (4) ignore platform-specific position limits ($50k typical), (5) apply equity corporate action logic (there are none), (6) use securities tax treatment when CFTC treatment may differ.

## Rules

1. **CFTC-regulated via designated contract markets.** Event contracts are offered through CFTC-registered DCMs (Kalshi, Robinhood Derivatives). They are NOT securities and are NOT regulated by SEC/FINRA. Different regulatory framework entirely.

2. **Binary payoff: $0 or $1.** Each contract settles at exactly $0 (event did not occur) or $1 (event occurred). There is no partial settlement, no continuous price at expiry. Current market price between $0.01 and $0.99 reflects probability.

3. **Fully collateralized — no margin.** To buy a "Yes" contract at $0.60, you pay $0.60 per contract. To sell (take the "No" side), you put up $0.40 per contract. Maximum loss equals the amount paid. There is NO leverage and NO margin.

4. **Position limits apply.** Platforms enforce position limits per event, typically $50,000 but varies. Some high-profile events (presidential elections) may have higher limits. Agents must check limits before sizing positions.

5. **Tax treatment is evolving.** The IRS has not issued definitive guidance. Event contracts may be treated as Section 1256 contracts (60/40 rule), ordinary income, or gambling winnings depending on the contract type and IRS interpretation. Consult a tax advisor. Do NOT assume capital gains treatment.

6. **No corporate actions.** Event contracts have no dividends, stock splits, mergers, or any other corporate action. Agents should skip all corporate action processing for event contract positions.

7. **Settlement on event outcome.** Contracts settle when the event occurs or at a predetermined settlement date — NOT at market close or on a rolling basis. Settlement is typically within 24 hours of the event outcome being determined.

8. **Event categories.** Common categories include:
   - Economics: Fed rate decisions, CPI, unemployment
   - Politics: Elections, policy outcomes
   - Weather: Temperature, hurricane landfall
   - Finance: Will S&P 500 close above X on date Y

9. **No short selling in the traditional sense.** Taking the "No" side of a contract is equivalent to selling, but you are buying the complementary outcome. Both sides are fully collateralized.

10. **Liquidity varies by event.** Popular events (Fed decisions, elections) have tight spreads. Obscure events may have wide spreads or no counterparty. Agents should check bid-ask spread before placing orders.

## Examples

### Position sizing with full collateralization
```
Event: "Will the Fed raise rates at the March meeting?"
Yes price: $0.35 (market implies 35% probability)
Budget: $1,000

Max contracts at $0.35: floor($1,000 / $0.35) = 2,857 contracts
If Yes: payout = 2,857 * $1.00 = $2,857 (profit = $1,857)
If No: payout = 2,857 * $0.00 = $0 (loss = $1,000)

No margin call possible — maximum loss is the $1,000 invested.
```

### Position limit check
```
Platform limit: $50,000 per event
Current exposure: $35,000 in "Yes" contracts on Fed rate decision
New order: $20,000 additional "Yes" contracts

$35,000 + $20,000 = $55,000 > $50,000 limit
Result: Order rejected or must be reduced to $15,000
```

## Agent Checklist

- [ ] Verify the asset is an event contract before applying any logic — skip all securities rules
- [ ] Never apply margin calculations — event contracts are fully collateralized
- [ ] Check platform position limits before placing orders
- [ ] Skip all corporate action processing for event contract positions
- [ ] Do not apply options Greeks or Black-Scholes pricing — binary payoff only
- [ ] Track settlement by event outcome, not market close
- [ ] Flag tax treatment as uncertain — do not assume capital gains or Section 1256
- [ ] Check bid-ask spread for liquidity before placing orders

## Structured Checks

```yaml
checks:
  - id: event_contract_position_limit
    condition: "asset_class != 'event_contract' OR event_contract_exposure <= event_contract_position_limit"
    severity: high
    message: "Event contract position exceeds platform position limit"
  - id: event_contract_no_margin
    condition: "asset_class != 'event_contract' OR event_contract_collateral >= event_contract_exposure"
    severity: critical
    message: "Event contracts must be fully collateralized — no margin available"
```

## Sources

- CFTC Event Contracts: https://www.cftc.gov/IndustryOversight/ContractMarkets/index.htm (accessed 2026-03-15)
- Kalshi Exchange Rules: https://kalshi.com/docs/exchange-rules (accessed 2026-03-15)
- Robinhood Predict: https://robinhood.com/us/en/about/predict/ (accessed 2026-03-15)
- CFTC Final Rule on Event Contracts (2024): https://www.cftc.gov/PressRoom/PressReleases/8990-24 (accessed 2026-03-15)
