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
26. **When offering direct indexing**, run the `direct-indexing` checker. Verify the account meets the minimum size threshold ($100K+). Cross-check every stock-level TLH sale against held ETFs tracking the same benchmark (wash sale risk). Monitor tracking error -- halt substitutions when it exceeds 2%.
27. **When facilitating copy trading**, run the `copy-trading` checker. Compare leader risk level against copier risk tolerance before enabling. Cap copy allocation to 25% of equity per leader. Block IRA accounts from copying margin/options strategies. Warn about size-ratio rounding distortion.
28. **When offering securities-based lending**, run the `margin-lending` checker. Monitor LTV against maintenance threshold continuously. Warn when LTV is within 5% of the threshold. Flag collateral concentration >50%. Validate loan purpose to prevent Regulation U violations.
29. **When managing income portfolios and RMDs**, run the `income-rmd` checker. Ensure RMD is scheduled for age 73+ traditional IRA/401(k) holders before December 31. Verify the scheduled amount meets the IRS minimum (prior year-end balance / Uniform Lifetime Table divisor). Flag withdrawal rates above 4% and equity allocations above 60% for age 73+.
30. **When trading event contracts / prediction markets**, run the `event-contracts` checker. Verify total exposure does not exceed platform position limits ($50K typical). Ensure full collateralization (no margin). Flag single-event concentration above 25% of equity and finance-category correlation above 10%.
31. **When managing cash and sweep programs**, run the `cash-management` checker. Track total deposits per bank (including external accounts) against the $250,000 FDIC limit. Flag idle cash above 5% for non-emergency accounts. Check SIPC $250K cash sublimit for money market sweeps.
32. **When managing custodial accounts (UTMA/UGMA)**, run the `custodial` checker. Block options, margin, futures, and short selling. Flag unearned income exceeding the $2,600 kiddie tax threshold. Alert when the minor is within 1 year of the state age of majority for irrevocable transfer preparation.
33. **When generating AI-powered investment content**, run the `ai-supervision` checker. Ensure every AI-generated message includes risk disclaimers (FINRA Rule 2210). Block return predictions and guarantees. Verify suitability analysis exists before recommendations. Confirm interaction logging and supervisory review are enabled.
34. **When including alternative investments in portfolios**, run the `alt-investments` checker. Verify accredited investor status for non-ETF alternatives. Enforce concentration cap (15-20%). Flag expense ratios above 1.0%. Verify customer experience level >= 3 for alt suitability.
35. **When trading or holding crypto assets**, run the `crypto` checker. Disclose that crypto is NOT covered by SIPC insurance. Track wash sales on digital assets (2025+ IRS rule). Flag staking rewards exceeding $600 YTD for 1099-MISC reporting. Monitor crypto allocation against concentration caps.
36. **When monitoring portfolio drift**, run the `portfolio-drift` checker. Compare current allocations against targets. Flag drift exceeding the rebalance threshold. Alert on severe drift (>2x threshold). Check that target allocations sum to 100%. Warn if last rebalance was more than 90 days ago.
37. **When applying ESG screening criteria**, run the `esg-screening` checker. Verify ESG-labeled funds do not hold excluded sector positions (greenwashing). Ensure ERISA accounts demonstrate financial materiality for ESG exclusions. Disclose the ESG rating provider. Monitor tracking error from exclusions.
38. **When deploying AI agents for customer interactions**, run the `adversarial-ai` checker. Ensure input sanitization, output validation, and prompt injection scanning are enabled. Detect system override attempts and data exfiltration patterns. Filter PII from model outputs. Maintain rate limiting and human escalation paths per FINRA 2026 guidance.
39. **When managing trust accounts**, run the `trust-accounts` checker. Enforce self-dealing prohibition on trustee transactions. Track estate tax exposure against the federal exclusion amount. Distinguish revocable (grantor's taxable estate) from irrevocable trusts. Monitor distribution sustainability (flag >7%). Track GSTT exemption allocation for generation-skipping transfers.

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
