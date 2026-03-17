---
id: "trading/regulations/futures-trading/rules"
title: "Futures Trading Rules"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - futures
  - cftc
  - nfa
  - initial-margin
  - maintenance-margin
  - mark-to-market
  - contract-expiration
  - section-1256
severity: "CRITICAL"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - futures-trading-systems
related:
  - "trading/regulations/pdt-rule/rules"
  - "trading/market-structure/t1-settlement/reference"
---

# Futures Trading Rules

## Summary

Futures contracts are regulated by the CFTC and NFA — NOT the SEC or FINRA. This means completely different rules for margin, day trading, taxation, and account protection. Agents that apply equity rules (PDT, Reg T, SIPC) to futures accounts will produce wrong results. Futures margin is per-contract performance bonds set by exchanges, not percentage-of-equity like Reg T. Margin calls must be resolved within hours, and 60/40 tax treatment applies regardless of holding period.

## The Problem

An agent built for equity trading that encounters futures will make critical errors: (1) applying PDT rules that do not exist for futures, (2) calculating margin as a percentage of position value instead of per-contract fixed amounts, (3) assuming T+1 or T+2 settlement when futures settle daily via mark-to-market, (4) applying standard capital gains tax rates when Section 1256 60/40 treatment applies, (5) not understanding that margin calls force liquidation within hours, not days. Each error can cause financial loss or missed compliance obligations.

## Rules

1. **CFTC regulates futures, NOT SEC/FINRA.** Futures are commodities contracts, not securities. The Commodity Futures Trading Commission (CFTC) and National Futures Association (NFA) are the regulators. FINRA rules (PDT, suitability, Reg T margin) do NOT apply.

2. **No PDT rule for futures.** Unlimited day trades are permitted regardless of account size. There is no 4-trade-in-5-days restriction. Cash accounts can day trade futures freely.

3. **Initial margin is per-contract, set by exchanges.** Unlike Reg T (50% of equity value), futures initial margin is a fixed dollar amount per contract set by the exchange (CME, ICE, etc.). Common amounts:
   - /ES (E-mini S&P 500): ~$12,650
   - /MES (Micro E-mini S&P 500): ~$1,265
   - /NQ (E-mini Nasdaq-100): ~$17,600
   - /MNQ (Micro E-mini Nasdaq-100): ~$1,760
   - /YM (E-mini Dow): ~$9,500
   - /CL (Crude Oil): ~$6,800
   - /GC (Gold): ~$10,500

4. **Maintenance margin is lower than initial margin.** If account equity drops below maintenance margin, a margin call is issued. The maintenance amount is typically 80-90% of initial margin.

5. **Margin calls are resolved within HOURS, not days.** Unlike equity margin calls (which allow 2-5 business days), futures margin calls can force liquidation the same day or next morning. Brokers will auto-liquidate without warning if maintenance margin is breached.

6. **Daily mark-to-market settlement.** Gains and losses settle in cash EVERY trading day. There is no "unrealized P&L" sitting in the account like equities — the account balance changes daily. A $5,000 loss on /ES today means $5,000 is debited from the account tonight.

7. **Day trade margin is ~50% of initial margin.** Most brokers offer reduced margin for intraday positions that are closed before the session ends. An /ES day trade might require ~$6,325 instead of $12,650. But the position MUST be closed before the session ends.

8. **Contract expiration requires action.** Futures contracts have specific expiration dates (typically third Friday of the contract month for index futures). Positions must be closed or rolled to the next contract before the delivery/settlement date. Failure to close can result in physical delivery obligations for commodity contracts or cash settlement for index contracts.

9. **Section 1256 tax treatment: 60/40 rule.** Regardless of how long a futures contract is held, gains/losses are taxed 60% as long-term capital gains and 40% as short-term capital gains. This is generally more favorable than equity short-term rates. Futures are also marked-to-market at year-end — open positions are treated as if sold on Dec 31.

10. **Not SIPC insured.** Futures accounts are not covered by SIPC (Securities Investor Protection Corporation). Customer funds are protected under CFTC segregation rules instead.

11. **Nearly 24-hour trading.** Most index futures trade from 6:00 PM ET Sunday to 5:00 PM ET Friday, with a daily maintenance break from 5:00 PM to 6:00 PM ET. This is nearly 23 hours per day, unlike equities (6.5 hours regular session).

12. **Short positions have same margin as long.** Unlike equities where short selling has additional requirements (locate, uptick rule), futures margin is identical for long and short positions.

## Examples

### Margin calculation for /ES
```
Position: Long 2 /ES contracts
Initial margin: 2 * $12,650 = $25,300
Maintenance margin: 2 * $11,500 = $23,000

Account balance: $28,000
Status: OK (above initial margin)

After a 50-point drop in S&P 500:
Loss: 2 contracts * 50 points * $50/point = $5,000
New balance: $28,000 - $5,000 = $23,000
Status: AT maintenance margin — any further drop triggers margin call
```

### Day trade margin example
```
Day trade 1 /ES contract:
Day trade margin: $12,650 * 50% = $6,325
Account balance needed: $6,325

MUST close before 5:00 PM ET or full overnight margin ($12,650) applies.
```

### Section 1256 tax treatment
```
Bought /ES on March 1, sold March 2 (held 1 day):
Profit: $2,000

Tax treatment (Section 1256):
- 60% long-term: $1,200 * 15% = $180
- 40% short-term: $800 * 37% = $296
- Total tax: $476

If this were a stock held 1 day:
- 100% short-term: $2,000 * 37% = $740

Savings from Section 1256: $264
```

## Agent Checklist

- [ ] Verify the account is a futures account before applying futures rules — NEVER apply PDT or Reg T
- [ ] Use per-contract margin amounts, not percentage-of-equity calculations
- [ ] Check maintenance margin per position — breach means liquidation within hours
- [ ] Track daily mark-to-market P&L — account balance changes every day
- [ ] Monitor contract expiration dates — roll or close 5+ days before expiration
- [ ] Apply Section 1256 60/40 tax treatment — do NOT use standard capital gains rates
- [ ] If day trading, ensure positions are closed before session end or margin doubles
- [ ] Use `abs(contracts)` for margin calculation — short and long have identical margin

## Structured Checks

```yaml
checks:
  - id: futures_margin_initial
    condition: "asset_class != 'futures' OR futures_account_balance >= futures_initial_margin_required"
    severity: critical
    message: "Insufficient balance for futures initial margin requirement"
  - id: futures_margin_maintenance
    condition: "asset_class != 'futures' OR futures_account_balance >= futures_maintenance_margin_required"
    severity: critical
    message: "Account below futures maintenance margin — margin call imminent (hours, not days)"
  - id: futures_expiration
    condition: "asset_class != 'futures' OR days_to_expiration > 5"
    severity: high
    message: "Futures contract approaching expiration — close or roll position"
```

## Sources

- CFTC About Futures Markets: https://www.cftc.gov/IndustryOversight/IndustryFilings/futures (accessed 2026-03-15)
- NFA Futures Disclosure Documents: https://www.nfa.futures.org/investors/investor-resources/index.html (accessed 2026-03-15)
- CME Group Margin Requirements: https://www.cmegroup.com/clearing/margins/outright-vol-scans.html (accessed 2026-03-15)
- IRS Section 1256 Contracts: https://www.irs.gov/publications/p550#en_US_2024_publink100010601 (accessed 2026-03-15)
- Robinhood Futures Trading: https://robinhood.com/us/en/about/futures/ (accessed 2026-03-15)
