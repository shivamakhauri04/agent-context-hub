---
id: "trading/portfolio-management/direct-indexing/rules"
title: "Direct Indexing and Stock-Level Tax-Loss Harvesting"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - direct-indexing
  - tax-loss-harvesting
  - wash-sale
  - tracking-error
  - custom-indexing
  - esg
severity: "CRITICAL"
last_verified: "2026-03-18"
applies_to:
  - trading-agents
  - robo-advisors
  - portfolio-management-systems
related:
  - "trading/regulations/tax-loss-harvesting/rules"
  - "trading/regulations/wash-sale/rules"
  - "trading/portfolio-management/automated-rebalancing/rules"
---

# Direct Indexing and Stock-Level Tax-Loss Harvesting

## Summary

Direct indexing replaces an index ETF with the individual stocks composing that index, enabling stock-level tax-loss harvesting (TLH) that multiplies the number of harvesting opportunities compared to ETF-level TLH. While Wealthfront and Schwab offer this for accounts $100K+, it introduces exponentially more complex wash sale tracking, tracking error management, and transaction cost analysis. Agents must understand that owning individual stocks AND an ETF tracking the same benchmark creates cross-holding wash sale risk that does not exist in pure ETF portfolios.

## The Problem

An agent that offers direct indexing without understanding the constraints will: (1) enable direct indexing on accounts too small to absorb the transaction costs, (2) harvest a loss on an individual stock while the investor still holds an ETF tracking the same index (wash sale), (3) allow tracking error to drift beyond acceptable bounds due to excessive TLH or ESG exclusions, (4) generate hundreds of trades per year where the commission and spread costs exceed the tax benefit, (5) fail to coordinate wash sale windows across hundreds of individual positions, and (6) create unmanageable tax lot complexity at year-end reporting.

## Rules

1. **Minimum account size thresholds are mandatory.** Direct indexing requires sufficient capital to hold a meaningful number of index constituents with reasonable position sizes. Accounts below $100,000 generally cannot achieve adequate diversification. Wealthfront requires $100K, Schwab requires $100K for their direct indexing product. Agents must not offer direct indexing below the configured minimum -- the transaction costs and tracking error overwhelm any TLH benefit at small sizes.

2. **Stock-level TLH multiplies wash sale complexity exponentially.** In an ETF portfolio with 5 ETFs, there are 5 potential wash sale pairs. In a direct index portfolio with 500 stocks, there are 500 potential wash sale pairs plus cross-holdings with any ETFs tracking overlapping benchmarks. Selling AAPL at a loss while holding VOO (which contains AAPL) is a wash sale because VOO is substantially identical at the component level. The agent must cross-check every individual stock sale against all held ETFs.

3. **Tracking error accumulates from TLH substitutions and exclusions.** Every time TLH substitutes one stock for another, or ESG/SRI screens exclude a stock, the portfolio drifts from its benchmark. Tracking error above 2% annualized indicates the portfolio no longer meaningfully replicates the index. The agent must monitor cumulative tracking error and halt further substitutions or exclusions when the threshold is breached.

4. **Transaction cost must exceed TLH benefit per trade.** Harvesting a $50 unrealized loss on a single stock position generates a maximum tax benefit of ~$18.50 (at 37% tax rate). If the round-trip transaction cost (commission + bid-ask spread) exceeds this benefit, the harvest destroys value. The agent must perform a cost-benefit check on each individual stock harvest, not just at the portfolio level.

5. **Rebalancing frequency must be constrained.** Daily TLH scans (as Wealthfront offers) can generate excessive trading. While daily scanning identifies more opportunities, executing all of them creates: (a) hundreds of tax lots per year, (b) short-term capital gains on replacement securities sold within a year, (c) wash sale window overlaps between consecutive harvests. The agent should enforce a minimum holding period between harvests of the same security.

6. **Cross-holding wash sale: individual stock + index ETF.** Owning AAPL directly AND holding an S&P 500 ETF (VOO, SPY, IVV) means selling AAPL at a loss while continuing to hold the ETF is problematic. The IRS has not issued definitive guidance on whether this constitutes a wash sale, but conservative compliance treats it as substantially identical. Agents must flag this overlap as a wash sale risk when the individual stock appears in the held ETF's benchmark index.

7. **ESG/SRI exclusions compound tracking error.** When an investor excludes fossil fuel, weapons, tobacco, or other sectors from a direct index portfolio, the tracking error increases proportionally to the excluded weight. Excluding the energy sector (~4% of S&P 500) adds approximately 0.3-0.5% tracking error. Multiple exclusion categories can push total tracking error above 2%. The agent must calculate the cumulative impact before applying exclusions.

## Examples

### Example 1: Wash sale with overlapping ETF
An investor holds 400 individual S&P 500 stocks via direct indexing and also holds VOO (Vanguard S&P 500 ETF) in another account. The agent harvests a $500 loss on AAPL in the direct index portfolio. Because VOO contains AAPL, this is a wash sale -- the loss is disallowed. The agent should have detected the ETF overlap before executing the harvest.

### Example 2: Below-minimum account
A $30,000 account requests direct indexing of the S&P 500. With 500 constituents, average position size would be $60. Transaction costs alone would consume most TLH benefits. The agent must refuse and recommend the ETF (VOO) instead.

### Example 3: Tracking error breach
After 18 months of TLH substitutions and ESG exclusions (no fossil fuels, no weapons), the portfolio's annualized tracking error reaches 3.2%. The agent should pause further substitutions and prioritize reducing tracking error through rebalancing.

## Agent Checklist

- [ ] Verify account meets minimum size threshold before offering direct indexing
- [ ] Cross-check every stock-level TLH sale against held ETFs for wash sale risk
- [ ] Monitor tracking error after each substitution or exclusion
- [ ] Calculate per-trade cost-benefit before executing stock-level harvests
- [ ] Enforce minimum interval between harvests of the same security
- [ ] Flag ESG/SRI exclusion impact on tracking error
- [ ] Coordinate wash sale windows across all 500+ individual positions

## Sources

- Wealthfront Direct Indexing: https://www.wealthfront.com/direct-indexing
- Schwab Personalized Indexing: https://www.schwab.com/personalized-indexing
- IRS Publication 550 (Wash Sales): https://www.irs.gov/publications/p550
- IRC Section 1091 (Wash Sales)
