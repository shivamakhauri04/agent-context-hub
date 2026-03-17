---
id: "trading/regulations/tax-loss-harvesting/rules"
title: "Tax-Loss Harvesting Rules"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - tax-loss-harvesting
  - wash-sale
  - capital-gains
  - replacement-securities
  - deduction-limit
  - year-end
severity: "HIGH"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - tax-loss-harvesting-systems
  - portfolio-management-systems
  - robo-advisors
related:
  - "trading/regulations/wash-sale/rules"
---

# Tax-Loss Harvesting Rules

## Summary

Tax-loss harvesting (TLH) is the strategy of selling securities at a loss to offset capital gains taxes, then buying a similar (but not substantially identical) replacement. Every major robo-advisor uses it. The strategy is constrained by the wash sale rule (30-day window), cross-account rules, spouse purchases, the $3,000 annual net loss deduction limit, and replacement security selection. Agents that harvest losses without understanding these constraints will trigger wash sales, permanently disallow losses, or violate IRS rules.

## The Problem

TLH agents commonly fail by: (1) selecting a replacement that is substantially identical (same index ETF), triggering a wash sale, (2) ignoring cross-account purchases (taxable + IRA = permanent loss disallowance), (3) not tracking spouse trades within the 30-day window, (4) harvesting losses in December without waiting 31+ days to repurchase, (5) not understanding that short-term losses are more valuable than long-term losses, (6) ignoring the $3,000 annual cap on net capital loss deductions. A single wash sale can negate an entire year of tax-loss harvesting.

## Rules

1. **Sell losing positions, buy substantially similar (NOT identical) replacements.** The core TLH strategy: sell security A at a loss, immediately buy security B that provides similar market exposure but is NOT substantially identical. The loss is deductible, and portfolio exposure is maintained.

2. **Replacement security selection is critical.** Common pairs and their wash sale risk:
   - Sell VOO (S&P 500), buy IVV (S&P 500): **RISKY** — same index, likely substantially identical
   - Sell VOO (S&P 500), buy VTI (Total Market): **SAFER** — different index
   - Sell AAPL, buy MSFT: **SAFE** — different companies, not substantially identical
   - Sell VXUS (Intl ex-US), buy IXUS (Intl ex-US): **RISKY** — same index
   - Sell AGG (US Agg Bond), buy SCHZ (US Agg Bond): **RISKY** — same index

3. **$3,000 annual net capital loss deduction limit.** If total capital losses exceed total capital gains, only $3,000 of net losses can be deducted against ordinary income per year ($1,500 if married filing separately). Excess carries forward indefinitely to future years.

4. **Short-term losses are more valuable.** Short-term capital losses offset short-term capital gains first, which are taxed at ordinary income rates (up to 37%). Long-term losses offset long-term gains taxed at 15-20%. Prioritize harvesting short-term losses when possible.

5. **Cross-account wash sale: IRA purchase permanently disallows the loss.** If you sell a security at a loss in a taxable account and buy it in an IRA within 30 days, the wash sale rule applies. But because the IRA has no cost basis tracking, the disallowed loss is PERMANENTLY lost — it is NOT added to the IRA position's basis.

6. **Spouse purchases trigger wash sale.** Per Revenue Ruling 2008-5, if your spouse buys the same or substantially identical security within 30 days of your loss sale, the wash sale rule applies. Agents must track spouse account trades.

7. **Year-end timing: 31+ days into January.** Losses harvested in December must avoid repurchase until at least 31 calendar days have passed. Selling Dec 15, buying back Jan 14 = wash sale (30 days). Must wait until Jan 15 or later.

8. **Tax alpha calculation.** Estimated tax savings = loss_amount * marginal_tax_rate. For a $10,000 short-term loss at 37% marginal rate: $10,000 * 0.37 = $3,700 tax savings. For long-term losses at 20%: $10,000 * 0.20 = $2,000.

9. **Crypto now subject to wash sale rules (2025+).** Starting in 2025, cryptocurrency is subject to the wash sale rule under the Infrastructure Investment and Jobs Act. Previously, crypto was exempt. Agents must now apply the 30-day window to crypto TLH.

10. **Partial harvesting is valid.** You can sell a portion of a losing position. If you own 1,000 shares of XYZ at a loss, selling 500 and buying a replacement for 500 is valid TLH (assuming no wash sale on the 500 sold).

11. **Carry-forward losses have no expiration.** Unused capital losses carry forward to future tax years indefinitely. An agent tracking TLH should maintain a running total of carry-forward losses.

## Examples

### Safe TLH pair selection
```
Portfolio holds: VOO (Vanguard S&P 500 ETF) at $10,000 unrealized loss

WRONG replacement: IVV (iShares S&P 500) — same index, substantially identical
RIGHT replacement: VTI (Vanguard Total Stock Market) — different index, broader exposure

Sell VOO, buy VTI immediately.
Loss of $10,000 is deductible.
Wait 31+ days before buying VOO back (if desired).
```

### Cross-account wash sale trap
```
Taxable account: Sell AAPL at $5,000 loss on March 1
IRA account: Buy AAPL on March 10

Result: Wash sale triggered.
The $5,000 loss is PERMANENTLY disallowed.
It cannot be added to the IRA position's cost basis.
The entire tax benefit is lost forever.
```

### Year-end TLH timeline
```
Dec 10: Sell QQQ at $8,000 loss (TLH)
Dec 10: Buy QQQM as replacement (different ETF, same Nasdaq-100 index — RISKY)

Better approach:
Dec 10: Sell QQQ at $8,000 loss
Dec 10: Buy VGT (Vanguard IT ETF) as replacement (different index)
Jan 10: 31 days have passed, can buy QQQ back if desired
```

### Tax alpha calculation
```
Losses harvested this year:
- TSLA: $8,000 short-term loss
- NVDA: $3,000 long-term loss
Total harvested: $11,000

Capital gains this year:
- AAPL: $5,000 short-term gain
- MSFT: $2,000 long-term gain
Total gains: $7,000

Net loss: $11,000 - $7,000 = $4,000
Deductible this year: $3,000 (annual cap)
Carry-forward to next year: $1,000

Tax savings this year:
- Offset $5,000 ST gain: $5,000 * 37% = $1,850
- Offset $2,000 LT gain: $2,000 * 20% = $400
- $3,000 deduction against ordinary income: $3,000 * 37% = $1,110
Total tax alpha: $3,360
```

## Agent Checklist

- [ ] Before harvesting, verify the replacement security is NOT substantially identical
- [ ] Check all accounts (taxable, IRA, spouse) for purchases within 30-day window
- [ ] Track the $3,000 annual net loss deduction limit and carry-forward balance
- [ ] Prioritize short-term losses over long-term losses for higher tax savings
- [ ] For December harvests, ensure no repurchase until 31+ calendar days have passed
- [ ] Apply wash sale rules to crypto positions (2025+)
- [ ] Calculate and log tax alpha for each harvest event
- [ ] Maintain a running carry-forward loss total across tax years

## Structured Checks

```yaml
checks:
  - id: tlh_wash_sale_guard
    condition: "days_since_loss_sale > 30 OR replacement_is_substantially_identical != 'true'"
    severity: critical
    message: "Tax-loss harvest at risk: replacement may be substantially identical within 30-day window"
  - id: tlh_cross_account_guard
    condition: "cross_account_purchase_within_30d != 'true'"
    severity: high
    message: "Cross-account wash sale risk: same security purchased in IRA/spouse account"
```

## Sources

- IRS Publication 550, Chapter 4 — Wash Sales: https://www.irs.gov/publications/p550 (accessed 2026-03-15)
- IRS Topic 409 — Capital Gains and Losses: https://www.irs.gov/taxtopics/tc409 (accessed 2026-03-15)
- Revenue Ruling 2008-5 (spouse wash sales): https://www.irs.gov/irb/2008-03_IRB#RR-2008-5 (accessed 2026-03-15)
- Infrastructure Investment and Jobs Act — crypto wash sale provision: https://www.congress.gov/bill/117th-congress/house-bill/3684 (accessed 2026-03-15)
