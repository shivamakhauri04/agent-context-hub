---
id: "trading"
title: "Trading & Finance Domain"
version: "1.0.0"
description: "Agent-readable knowledge for algorithmic trading, portfolio management, and financial compliance."
categories:
  - data-vendors
  - regulations
  - corporate-actions
  - broker-apis
  - technical-indicators
  - market-structure
  - order-execution
  - portfolio-management
maintainers: ["shivamakhauri"]
---

# Trading & Finance Domain

## Purpose

This domain provides structured, machine-readable knowledge that AI agents need when building, operating, or debugging algorithmic trading systems. Every document captures hard-won lessons, regulatory constraints, and vendor-specific quirks that are difficult to learn from API docs alone.

## Taxonomy of Categories

### data-vendors
Gotchas, quirks, and reliability notes for market data providers (yfinance, Polygon, Alpha Vantage, etc.). Covers data quality issues, rate limits, schema changes, and silent failure modes.

### regulations
Financial regulations that directly affect automated trading logic. Includes FINRA rules (PDT), IRS rules (wash sales), and SEC requirements. These are compliance-critical — violations carry real financial and legal consequences.

### corporate-actions
Events like stock splits, dividends, mergers, and spin-offs that alter price history, position sizes, and order parameters. Agents must detect and handle these to avoid catastrophic misinterpretation of price data.

### broker-apis
Broker-specific integration notes for Alpaca, Interactive Brokers, TD Ameritrade, and others. Covers order lifecycle quirks, environment differences (paper vs live), and undocumented behaviors.

### technical-indicators
Calculation pitfalls for common indicators (VWAP, RSI, MACD, etc.). Focuses on mistakes agents commonly make — wrong timeframe assumptions, reset boundaries, and data requirements.

### market-structure
Reference data for trading hours, exchange rules, tick sizes, and session boundaries. Essential for any agent that needs to know when markets are open and how liquidity varies.

### order-execution
Order lifecycle and execution, order types, time-in-force options, and fill quality. Covers best execution requirements, slippage, and broker-specific execution behavior.

### portfolio-management
Automated portfolio management features: rebalancing, recurring investments (DCA), asset allocation, and drift monitoring. Core robo-advisor functionality.

## How Agents Should Use This Content

1. **Before making API calls** to a data vendor or broker, read the relevant gotchas/quirks document.
2. **Before executing trades**, check the regulations category for applicable rules (especially PDT and wash sale).
3. **When price data looks anomalous** (large gaps, sudden drops), consult corporate-actions before assuming a crash.
4. **When computing indicators**, verify your calculation approach against the technical-indicators docs.
5. **When scheduling trades**, reference market-structure for hours, holidays, and session types.
6. **When managing IRA accounts**, check contribution limits, Roth income eligibility, and early withdrawal penalties before any transaction.
7. **When trading crypto**, do not apply equity rules (PDT, SIPC, NBBO) — crypto has its own regulatory framework.
8. **When placing fractional/odd-lot orders**, acknowledge NBBO is not guaranteed and check transfer restrictions.
9. **When generating customer-facing AI content**, ensure compliance with FINRA Rule 2210 — include risk disclaimers, avoid return predictions.
10. **When trading futures**, use CFTC/NFA rules — NOT SEC/FINRA. Margin is per-contract, not percentage-of-equity. No PDT rule applies.
11. **When encountering event contracts / prediction markets**, treat as binary CFTC-regulated instruments — no margin, no corporate actions, fully collateralized.
12. **When performing tax-loss harvesting**, verify replacement securities are not substantially identical, check cross-account and spouse purchases, respect the $3,000 annual deduction limit.
13. **When evaluating leveraged/inverse ETFs**, warn about daily reset and volatility drag — not suitable for buy-and-hold per FINRA Notice 09-31.
14. **When calculating settlement dates**, use T+1 (not T+2) for US equities since May 28, 2024. Audit any hardcoded T+2 values.
15. **When trading in cash accounts**, track settled vs unsettled cash to avoid Good Faith Violations. Three GFV in 12 months freezes the account for 90 days.
16. **When short selling**, always confirm locate before submitting orders. Check Reg SHO threshold securities list, monitor borrow rates, and track close-out deadlines.
17. **When rebalancing portfolios**, check for wash sale conflicts, enforce minimum trade sizes, and wait for prior trades to settle before rebalancing again.
18. **When trading 0DTE options**, cap total exposure to a fixed % of equity, verify exercise capital for short positions, and monitor gamma exposure in real-time.
19. **When managing recurring investments (DCA)**, verify sufficient funds before each scheduled buy, check for wash sale conflicts with recent loss sales, and coordinate with DRIP.
20. **When selecting order types**, use limit orders for illiquid securities and extended hours, understand stop-limit vs stop-market gap risk, and verify broker support for advanced types (bracket, OCO).
21. **When performing tax-loss harvesting**, run the `tlh` checker to validate replacement securities are not substantially identical, verify no cross-account IRA purchases within 30 days, and confirm net losses don't exceed the $3,000 annual deduction limit without carryforward tracking.
22. **When constructing goal-based portfolios**, run the `goal-allocation` checker. Emergency funds must be 100% cash. Short-term goals (<3yr) max 30% equity. Match risk score to allocation. Separate goals into distinct buckets.
23. **When optimizing asset location across accounts**, run the `asset-location` checker. Place bonds and REITs in tax-advantaged accounts, keep municipal bonds in taxable, and put highest-growth assets in Roth IRA.
24. **When recommending strategies to customers**, run the `suitability` checker. Never recommend strategies with risk levels exceeding customer tolerance. Monitor turnover ratio for churning (>6 is red flag). Flag single-position concentrations >25%.
25. **When managing DRIP settings**, run the `drip` checker. Disable DRIP on any security before tax-loss harvesting it. Check for DRIP + DCA overlap (double-buying). Remember each DRIP purchase creates a separate tax lot and 30-day wash sale window.

## Severity Levels

| Severity | Meaning |
|----------|---------|
| CRITICAL | Can cause financial loss, regulatory violation, or silently corrupt data. Must be checked every time. |
| HIGH | Can cause incorrect behavior or degraded performance. Should be checked on first use and periodically. |
| MEDIUM | Good to know. Reduces debugging time and improves robustness. |
| LOW | Nice-to-have context. Helpful for optimization. |

## Document Format

Every content document in this domain follows a consistent structure:
- **YAML frontmatter**: metadata for programmatic discovery and filtering
- **Summary**: one-paragraph overview
- **The Problem**: what goes wrong if this knowledge is missing
- **Rules**: numbered, actionable directives
- **Examples**: real-world code or scenarios with real tickers and dates
- **Agent Checklist**: quick pre-flight checks an agent can run
- **Sources**: authoritative references for verification
