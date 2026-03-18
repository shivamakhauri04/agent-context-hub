---
id: "trading/portfolio-management/income-portfolio/rules"
title: "Income Portfolios and Required Minimum Distributions (RMD)"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - rmd
  - income-portfolio
  - retirement
  - withdrawal-strategy
  - sequence-of-returns
  - bucket-strategy
severity: "CRITICAL"
last_verified: "2026-03-18"
applies_to:
  - trading-agents
  - robo-advisors
  - retirement-planning-systems
related:
  - "trading/regulations/ira-retirement/rules"
  - "trading/portfolio-management/goal-based-allocation/rules"
  - "trading/portfolio-management/asset-location/rules"
---

# Income Portfolios and Required Minimum Distributions (RMD)

## Summary

Income-focused portfolios serve retirees who need regular cash flow from their investments. Fidelity Go and other robo-advisors target this segment with automated income strategies. The most critical regulatory requirement is the Required Minimum Distribution (RMD) -- mandatory annual withdrawals from traditional IRA and 401(k) accounts starting at age 73 (SECURE 2.0 Act). Missing an RMD triggers a 25% excise tax on the shortfall (reduced from 50% by SECURE 2.0), or 10% if corrected within 2 years. Beyond RMDs, agents must manage sequence-of-returns risk, withdrawal rate sustainability, and the allocation glide path from growth to income.

## The Problem

An agent managing income portfolios without understanding RMD rules and withdrawal strategies will: (1) miss the RMD deadline (December 31), triggering a 25% excise tax penalty on the shortfall, (2) calculate the wrong RMD amount by using the wrong year-end balance or IRS table, (3) maintain an equity allocation too high for the investor's age and withdrawal needs (sequence-of-returns risk), (4) recommend a withdrawal rate above 4% without stress-testing for market downturns, (5) rely solely on dividend income rather than a total-return withdrawal strategy, (6) fail to implement a bucket strategy that separates near-term cash needs from long-term growth, and (7) miss Roth conversion opportunities in low-income years before RMDs begin.

## Rules

1. **RMD is required from traditional IRA/401(k) starting at age 73.** The SECURE 2.0 Act (2022) raised the RMD starting age from 72 to 73 (effective 2023) and will raise it to 75 in 2033. Roth IRAs have no RMD requirement during the owner's lifetime. Inherited IRAs and Roth 401(k)s had RMD requirements but SECURE 2.0 eliminates Roth 401(k) RMDs starting 2024. The agent must track the account holder's age and account type to determine if RMD applies.

2. **RMD penalty is 25% excise tax on the shortfall.** SECURE 2.0 reduced the penalty from 50% to 25%, and further to 10% if the shortfall is corrected within 2 years. Despite the reduction, this is still one of the harshest tax penalties in the IRS code. If an investor must take $20,000 RMD and takes $0, the penalty is $5,000 (25%) or $2,000 (10% if corrected within 2 years). The agent must ensure RMD is scheduled and the amount meets the minimum.

3. **RMD calculation: prior year-end balance divided by IRS life expectancy divisor.** The RMD for a given year = account balance as of December 31 of the prior year / Uniform Lifetime Table divisor for the account holder's age. For age 73, the divisor is 26.5, so a $500,000 balance requires $18,868 RMD. The agent must use the correct table (Uniform Lifetime Table for most, Joint Life Table if spouse is sole beneficiary and >10 years younger).

4. **Sequence-of-returns risk is the primary threat to income portfolios.** Withdrawing from a portfolio during a market drawdown permanently impairs the portfolio's ability to recover. A 30% drop followed by a 30% recovery does not return to the starting value -- the investor is down 9% before accounting for withdrawals. High equity allocations (>60%) for age 73+ investors amplify this risk. The agent should flag portfolios with high equity allocation relative to the investor's age and withdrawal rate.

5. **Sustainable withdrawal rate guidelines.** The "4% rule" (Bengen 1994) suggests withdrawing 4% of the initial portfolio value annually (inflation-adjusted) for a 30-year retirement. Withdrawal rates above 4% in non-RMD contexts increase the probability of portfolio depletion. The agent should warn when the withdrawal rate exceeds 4% and is not driven by RMD requirements, as RMDs may force higher rates for older investors.

6. **Total return withdrawal beats dividend-only income.** Relying solely on dividends for income forces the portfolio into high-yield, low-growth positions. A total-return approach (selling appreciated positions as needed) provides more flexibility, better diversification, and potentially better after-tax results. The agent should not construct a portfolio that concentrates in high-dividend stocks solely to avoid selling shares.

7. **Bucket strategy: separate time horizons.** The bucket approach divides the portfolio into: (a) short-term bucket (1-2 years of expenses in cash/money market), (b) intermediate bucket (3-7 years in bonds/fixed income), (c) long-term bucket (8+ years in equities for growth). During market downturns, the investor draws from the cash bucket while equities recover. The agent should implement and monitor bucket allocations.

8. **Roth conversion ladder before RMDs.** In the years between retirement and age 73, when income is typically low, converting traditional IRA assets to Roth IRA can reduce future RMDs and provide tax-free growth. The conversion is taxed as ordinary income in the conversion year, but at a potentially lower rate than future RMD-forced distributions. The agent should identify Roth conversion opportunities in low-income years.

## Examples

### Example 1: Missed RMD
Investor age 75, traditional IRA balance $400,000 at prior year-end. Divisor for age 75 is 24.6. Required RMD = $16,260. Investor has not scheduled any distribution by November. Agent must flag CRITICAL -- missing the December 31 deadline triggers $4,065 penalty (25%).

### Example 2: High withdrawal rate
Investor age 68 (pre-RMD), portfolio $800,000, requesting $48,000/year withdrawal (6% rate). No RMD requirement yet. Agent should warn that 6% withdrawal rate significantly exceeds the 4% guideline and increases portfolio depletion risk.

### Example 3: High equity for retiree
Investor age 76, 75% equity allocation, taking RMDs. A 30% market correction would reduce the portfolio by 22.5% while the investor continues withdrawing. Agent should flag that equity allocation >60% at age 73+ is aggressive for an income portfolio.

## Agent Checklist

- [ ] Check if RMD is required (age >= 73, traditional IRA/401k)
- [ ] Verify RMD amount meets the calculated minimum (prior year-end balance / divisor)
- [ ] Ensure RMD is scheduled before December 31 deadline
- [ ] Flag withdrawal rates above 4% in non-RMD contexts
- [ ] Warn if equity allocation exceeds 60% for age 73+ investors
- [ ] Implement bucket strategy for near-term cash needs
- [ ] Identify Roth conversion opportunities in low-income pre-RMD years
- [ ] Use total-return withdrawal strategy, not dividend-only

## Sources

- SECURE 2.0 Act (2022): https://www.congress.gov/bill/117th-congress/house-bill/2617
- IRS Uniform Lifetime Table: https://www.irs.gov/publications/p590b
- IRS Publication 590-B (Distributions from IRAs)
- Bengen, William P. (1994) "Determining Withdrawal Rates Using Historical Data"
- Fidelity Go Income Planning: https://www.fidelity.com/managed-accounts/fidelity-go/overview
