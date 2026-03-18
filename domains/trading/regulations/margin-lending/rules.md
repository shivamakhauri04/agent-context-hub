---
id: "trading/regulations/margin-lending/rules"
title: "Securities-Based Lending and Margin Lending"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - margin-lending
  - securities-based-lending
  - ltv
  - forced-liquidation
  - regulation-u
  - collateral
severity: "CRITICAL"
last_verified: "2026-03-18"
applies_to:
  - trading-agents
  - robo-advisors
  - wealth-management-systems
related:
  - "trading/regulations/margin-requirements/rules"
  - "trading/portfolio-management/automated-rebalancing/rules"
---

# Securities-Based Lending and Margin Lending

## Summary

Securities-based lending (SBL) allows investors to borrow against their portfolio as collateral without selling positions. All major brokers (Schwab, Fidelity, Interactive Brokers) offer this. Unlike margin for trading (covered by the existing margin checker), SBL is a general-purpose loan product with its own LTV ratios, maintenance requirements, forced liquidation rules, and Regulation U restrictions. The key risk is forced liquidation during market downturns -- the broker chooses what to sell, not the investor, and the timing is the worst possible.

## The Problem

An agent that facilitates securities-based lending without understanding the constraints will: (1) allow borrowing up to the maximum LTV, leaving no buffer for market declines, (2) fail to warn when LTV approaches the maintenance threshold triggering forced liquidation, (3) ignore concentration limits that reduce effective LTV for single-stock portfolios, (4) permit loan proceeds to purchase additional securities (Regulation U violation for non-purpose loans), (5) underestimate forced liquidation risk during volatile markets (VIX spikes reduce collateral value rapidly), and (6) miscalculate interest costs that accrue continuously and reduce effective returns.

## Rules

1. **Loan-to-value (LTV) ratios depend on collateral type.** Typical LTV: 50-70% for diversified equity portfolios, 50-65% for concentrated single-stock, 70-80% for investment-grade bonds, 0% for penny stocks and illiquid securities. The agent must never allow borrowing above the maintenance LTV threshold -- when `loan_balance / collateral_value > maintenance_ltv_pct`, forced liquidation begins immediately.

2. **Margin call mechanics trigger forced liquidation.** When collateral value drops and LTV exceeds the maintenance threshold, the broker issues a margin call. If not met within the deadline (often same-day for SBL), the broker liquidates collateral at market prices. The broker chooses which positions to sell -- not the investor. This often means selling the most liquid positions (typically the investor's best holdings) at the worst possible time (market decline).

3. **Concentration limits reduce effective LTV.** A portfolio with >50% in a single position faces reduced LTV because the collateral is undiversified. A single-stock portfolio might only get 30-40% LTV instead of the standard 50-70%. The agent must flag concentration above 50% and adjust LTV expectations accordingly.

4. **Regulation U prohibits using non-purpose loan proceeds to buy securities.** SBL loans designated as "non-purpose" (general use: home renovation, tax payment, bridge financing) cannot be used to purchase margin stock. Using SBL proceeds to buy more securities is a Regulation U violation. The agent must validate loan purpose and block securities purchases with SBL proceeds when the loan is non-purpose.

5. **Interest accrues continuously at variable rates.** SBL interest rates are variable, tied to a benchmark (typically Fed Funds + spread), and accrue daily. Rates are tiered by loan balance -- larger loans get better rates. The interest is not automatically tax-deductible; deductibility depends on loan purpose (investment interest is deductible against net investment income under IRC Section 163(d), but personal-use interest is not). The agent must track accrued interest and its tax treatment.

6. **Volatile markets amplify liquidation risk.** A VIX spike from 15 to 40 can reduce collateral value by 20-30% in days. If the investor is at 60% LTV and collateral drops 25%, LTV jumps to 80% -- well above any maintenance threshold. The agent should monitor market volatility and warn when LTV is within 5% of the maintenance threshold, even if not currently in violation.

7. **Forced liquidation creates taxable events.** When the broker force-liquidates positions, each sale is a taxable event. If the positions have significant unrealized gains, the tax bill compounds the loss from the market decline. The agent should factor in the tax cost of potential forced liquidation when assessing whether to take an SBL loan.

8. **Interest deductibility follows net investment income rules.** Investment interest expense (from loans used to buy investments) is deductible only up to net investment income (dividends + interest + short-term capital gains). Excess investment interest carries forward. Personal-use SBL interest is never deductible. The agent must not promise tax benefits without validating the loan purpose and the investor's net investment income.

## Examples

### Example 1: LTV breach during downturn
Investor borrows $300K against a $500K portfolio (60% LTV). Maintenance LTV is 70%. Market drops 20%, portfolio falls to $400K. New LTV = $300K / $400K = 75%. Margin call triggered. Broker force-liquidates $100K of positions at depressed prices.

### Example 2: Reg U violation
Investor takes a $200K SBL loan marked as "general purpose." Uses $50K to buy AAPL stock. This violates Regulation U -- the loan was designated non-purpose but proceeds were used to purchase margin stock.

### Example 3: Concentration penalty
Investor holds $1M in a single stock (TSLA). Standard SBL LTV would be 60% ($600K available). Due to concentration (100% single stock), broker reduces LTV to 35% ($350K available). Agent must reflect the reduced LTV.

## Agent Checklist

- [ ] Check current LTV against maintenance threshold before any action
- [ ] Warn when LTV is within 5% of maintenance threshold
- [ ] Flag concentration >50% in a single position (reduced LTV)
- [ ] Validate loan purpose -- block securities purchases with non-purpose loans
- [ ] Calculate and disclose continuous interest accrual
- [ ] Factor in tax impact of potential forced liquidation
- [ ] Monitor market volatility (VIX) for amplified liquidation risk
- [ ] Track interest deductibility based on loan purpose and net investment income

## Sources

- Federal Reserve Regulation U: https://www.ecfr.gov/current/title-12/chapter-II/subchapter-A/part-221
- FINRA Margin Requirements: https://www.finra.org/rules-guidance/key-topics/margin-accounts
- IRC Section 163(d) (Investment Interest Deduction)
- SEC Securities-Based Lending Guidance
