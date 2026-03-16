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

## How Agents Should Use This Content

1. **Before making API calls** to a data vendor or broker, read the relevant gotchas/quirks document.
2. **Before executing trades**, check the regulations category for applicable rules (especially PDT and wash sale).
3. **When price data looks anomalous** (large gaps, sudden drops), consult corporate-actions before assuming a crash.
4. **When computing indicators**, verify your calculation approach against the technical-indicators docs.
5. **When scheduling trades**, reference market-structure for hours, holidays, and session types.

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
