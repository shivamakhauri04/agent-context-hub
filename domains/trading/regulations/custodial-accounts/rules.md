---
id: "trading/regulations/custodial-accounts/rules"
title: "Custodial Accounts (UTMA/UGMA)"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - custodial
  - utma
  - ugma
  - minor
  - kiddie-tax
  - fiduciary
severity: "HIGH"
last_verified: "2026-03-19"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - robo-advisors
related:
  - "trading/regulations/ira-retirement/rules"
  - "trading/regulations/suitability/rules"
---

# Custodial Accounts (UTMA/UGMA)

## Summary

Custodial accounts under the Uniform Transfers to Minors Act (UTMA) or Uniform Gifts to Minors Act (UGMA) allow adults to hold and manage assets on behalf of a minor until the minor reaches the age of majority. These accounts carry strict fiduciary obligations, prohibited instrument restrictions, tax implications (kiddie tax), and an irrevocable transfer requirement at majority. Agents that treat custodial accounts like standard brokerage accounts will violate fiduciary duties, execute prohibited trades, or mishandle the tax consequences of minor's investment income.

## The Problem

An agent managing a custodial account without proper checks will: (1) execute options, margin, futures, or short selling trades that are prohibited in custodial accounts, (2) fail to flag unearned income exceeding the kiddie tax threshold, causing unexpected tax liability at the parent's marginal rate, (3) miss the approaching age of majority, leaving assets in limbo or failing to prepare for the irrevocable transfer, (4) invest speculatively in violation of the custodian's fiduciary duty to the minor, (5) incorrectly calculate FAFSA impact by treating custodial assets like parent assets.

## Rules

1. **UTMA/UGMA gifts are irrevocable.** Once assets are placed in a custodial account, they belong to the minor. The custodian cannot take them back. This is a completed gift for tax purposes.

2. **Custodian has fiduciary duty to invest for the minor's benefit.** The custodian must manage assets prudently and solely for the minor's benefit. Speculative trading, excessive risk-taking, and self-dealing are prohibited.

3. **Prohibited instruments in custodial accounts: options, margin, futures, short selling.** Most brokerages prohibit these in custodial accounts because they involve leverage or unlimited loss potential, which conflicts with the fiduciary duty. The agent must block any attempt to trade these instruments.

4. **Kiddie Tax applies to unearned income above thresholds.** For 2025-2026: the first $1,300 of a minor's unearned income (dividends, interest, capital gains) is tax-free. The next $1,300 is taxed at the child's rate. Unearned income above $2,600 is taxed at the parent's marginal rate. This can significantly increase the tax burden if the portfolio generates substantial income.

5. **Age of majority varies by state (18-25).** UTMA allows states to set the age of majority between 18 and 25 (most states use 18 or 21). At this age, the custodial arrangement terminates and all assets transfer irrevocably to the now-adult beneficiary. The agent should track the minor's age and alert when transfer is approaching.

6. **Transfer at majority is mandatory and irrevocable.** When the minor reaches the age of majority, the custodian must transfer all assets. The custodian cannot delay, withhold, or add conditions. The beneficiary gets full control regardless of maturity or financial literacy.

7. **Cannot offset minor's capital losses against parent's income.** Capital losses in a custodial account can only offset the minor's own capital gains and up to $3,000 of the minor's ordinary income. They cannot be used on the parent's tax return.

8. **FAFSA treats custodial assets at 20% rate.** Assets in a custodial account are considered the student's assets for financial aid purposes and are assessed at 20% (vs. 5.64% for parent assets). This can significantly reduce financial aid eligibility.

## Examples

### Prohibited instrument check
```
Account: UTMA custodial for 14-year-old
Pending order: Buy 5 TSLA call options

Result: BLOCKED — options trading is prohibited in custodial accounts.
Custodian fiduciary duty requires conservative management for the minor's benefit.
```

### Kiddie tax calculation
```
Minor age: 16
Unearned income YTD: $4,000

Tax breakdown:
  First $1,300: tax-free
  Next $1,300: child's rate (10% = $130)
  Remaining $1,400: parent's marginal rate (e.g., 32% = $448)

Total tax: $578 (vs. $400 if all at child's rate)
Agent should flag when unearned income exceeds $2,600.
```

## Agent Checklist

- [ ] Verify account is custodial before executing any trade
- [ ] Block options, margin, futures, and short selling in custodial accounts
- [ ] Monitor unearned income against $2,600 kiddie tax threshold
- [ ] Track minor's age relative to state age of majority
- [ ] Alert custodian when minor is within 1 year of age of majority
- [ ] Never treat custodial assets as parent's assets for tax calculations
- [ ] Factor in 20% FAFSA assessment rate when advising on college savings
- [ ] Ensure all investments align with fiduciary duty (prudent, for minor's benefit)

## Sources

- Uniform Transfers to Minors Act (UTMA): State-by-state variations
- IRS Publication 929: Tax Rules for Children and Dependents (Kiddie Tax)
- FAFSA: Federal Student Aid — Treatment of Student vs. Parent Assets
- Robinhood Custodial Accounts: https://robinhood.com/us/en/about/custodial/ (accessed 2026-03-19)
- Schwab Custodial Account Guide: https://www.schwab.com/custodial-account (accessed 2026-03-19)
