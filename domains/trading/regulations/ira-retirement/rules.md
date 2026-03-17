---
id: "trading/regulations/ira-retirement/rules"
title: "IRA / Retirement Account Rules"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - ira
  - roth-ira
  - traditional-ira
  - retirement
  - contribution-limits
  - early-withdrawal
  - rmd
  - irs
severity: "CRITICAL"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - retirement-planning-tools
related:
  - "trading/regulations/wash-sale/rules"
  - "trading/regulations/options-trading/rules"
---

# IRA / Retirement Account Rules

## Summary

Individual Retirement Accounts (IRAs) have hard IRS-enforced limits on contributions, income eligibility (Roth), withdrawals, and tax treatment. Violations carry automatic penalties — a 6% excise tax on excess contributions and a 10% early withdrawal penalty — that cannot be negotiated or appealed. An agent managing IRA accounts MUST enforce these limits programmatically. Unlike brokerage rules that produce warnings, IRA violations produce IRS tax penalties.

## The Problem

An agent that treats an IRA like a regular brokerage account will cause direct financial harm to the account holder. The most dangerous mistakes: (1) over-contributing beyond the annual limit triggers a 6% excise tax every year the excess remains, (2) allowing Roth contributions when MAGI exceeds the phase-out creates excess contributions that must be recharacterized or withdrawn, (3) triggering early withdrawals without warning about the 10% penalty, (4) not recognizing that wash sales across IRA and taxable accounts permanently disallow the loss (not just defer it). These are not broker-level restrictions — they are IRS tax code violations with automatic penalties.

## Rules

1. **Annual contribution limit: $7,000 (under 50) / $8,000 (50+) for 2025-2026.** This limit applies across ALL IRAs combined (Traditional + Roth). Contributing to both a Traditional and Roth IRA in the same year is allowed, but the total cannot exceed the limit. Excess contributions incur a 6% excise tax (IRS Form 5329) for every year the excess remains in the account.

2. **Roth IRA income phase-out (MAGI).** For 2025-2026: Single filers phase out at $150,000-$165,000 MAGI. Married filing jointly: $236,000-$246,000. Above the upper limit, no Roth contributions are allowed. Within the phase-out range, the allowed contribution is reduced proportionally. Married filing separately: $0-$10,000 phase-out (effectively disqualified).

3. **Early withdrawal penalty: 10% before age 59.5.** Withdrawals of earnings (Roth) or any amount (Traditional) before age 59.5 incur a 10% penalty on top of ordinary income tax. Exceptions: first home purchase ($10,000 lifetime max), qualified education expenses, disability, substantially equal periodic payments (72(t)), medical expenses exceeding 7.5% of AGI.

4. **Traditional IRA Required Minimum Distributions (RMDs).** Starting at age 73 (SECURE 2.0 Act), Traditional IRA holders must begin taking required minimum distributions. Failure to take RMDs triggers a 25% excise tax on the amount not distributed (reduced from 50% by SECURE 2.0). Roth IRAs have NO RMD requirement during the owner's lifetime.

5. **Roth IRA 5-year rule for earnings withdrawal.** Even after age 59.5, Roth earnings are only tax-free if the account has been open for at least 5 tax years. Contributions can always be withdrawn tax-free (they were made with after-tax dollars). Conversions have their own 5-year clock.

6. **Options in IRAs: cash-secured only, no margin.** IRAs cannot use margin. Allowed strategies: covered calls, cash-secured puts, long calls/puts, and some spreads (broker-dependent). Naked options and short selling are prohibited. The agent must verify that any options strategy is cash-secured before execution.

7. **Wash sale across IRA and taxable accounts: loss is PERMANENTLY disallowed.** If a security is sold at a loss in a taxable account and a substantially identical security is purchased in an IRA within 30 days, the loss is permanently disallowed — it cannot be added to the IRA's cost basis (unlike taxable-to-taxable wash sales where the loss is deferred). This is one of the most dangerous cross-account interactions.

8. **Robinhood IRA match: 1-3% on contributions.** Robinhood offers a 1% match (3% for Gold subscribers) on IRA contributions. The match has a 5-year vesting schedule — unvested match is forfeited on transfer. The match counts toward the annual contribution limit from Robinhood's side, not the user's.

## Examples

### Contribution limit tracking
```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class IRAContributionTracker:
    """Track IRA contributions against annual limits."""
    age: int
    ytd_traditional: Decimal = Decimal("0")
    ytd_roth: Decimal = Decimal("0")

    @property
    def limit(self) -> Decimal:
        return Decimal("8000") if self.age >= 50 else Decimal("7000")

    @property
    def total_contributed(self) -> Decimal:
        return self.ytd_traditional + self.ytd_roth

    @property
    def remaining(self) -> Decimal:
        return max(Decimal("0"), self.limit - self.total_contributed)

    def can_contribute(self, amount: Decimal) -> bool:
        return self.total_contributed + amount <= self.limit
```

### Roth income check
```python
def roth_max_contribution(magi: float, filing_status: str, age: int) -> float:
    """Calculate maximum Roth IRA contribution based on MAGI."""
    base_limit = 8000.0 if age >= 50 else 7000.0

    if filing_status == "single":
        lower, upper = 150000, 165000
    elif filing_status == "married_filing_jointly":
        lower, upper = 236000, 246000
    elif filing_status == "married_filing_separately":
        lower, upper = 0, 10000
    else:
        return base_limit  # Conservative: allow full

    if magi <= lower:
        return base_limit
    if magi >= upper:
        return 0.0
    # Proportional reduction in phase-out range
    reduction_factor = (magi - lower) / (upper - lower)
    return round(base_limit * (1 - reduction_factor), 2)
```

### Cross-IRA wash sale trap
```
Scenario:
Day 1:  Sell 100 AAPL at loss (-$2,000) in taxable account
Day 15: Buy 100 AAPL in Roth IRA (within 30-day window)

Result: $2,000 loss is PERMANENTLY disallowed.
- Cannot add to Roth cost basis (IRS does not allow)
- Cannot defer to future sale (unlike taxable wash sale)
- The $2,000 tax deduction is gone forever
```

## Agent Checklist

- [ ] Track YTD contributions across ALL IRA accounts (Traditional + Roth combined)
- [ ] Before any contribution, verify remaining room under annual limit
- [ ] For Roth contributions, verify MAGI is below the phase-out upper limit
- [ ] Before any withdrawal, check account holder age against 59.5 threshold
- [ ] For Traditional IRA holders age 73+, ensure RMD has been taken
- [ ] When selling at a loss in taxable account, check for IRA purchases within 30 days
- [ ] Verify options strategies are cash-secured (no margin in IRA)
- [ ] Track Roth 5-year rule for earnings withdrawals

## Structured Checks

```yaml
checks:
  - id: ira_contribution_limit
    condition: "ira_contribution_ytd <= 7000 OR account_holder_age >= 50"
    severity: critical
    message: "IRA contribution exceeds annual limit — 6% IRS excise tax on excess"
  - id: ira_roth_income_eligibility
    condition: "ira_type != 'roth' OR magi <= 165000"
    severity: critical
    message: "MAGI exceeds Roth IRA eligibility — contributions not allowed"
  - id: ira_early_withdrawal
    condition: "withdrawal_amount == 0 OR account_holder_age >= 59.5"
    severity: high
    message: "IRA withdrawal before 59.5 incurs 10% early withdrawal penalty"
```

## Sources

- IRS Publication 590-A (Contributions to IRAs): https://www.irs.gov/publications/p590a
- IRS Publication 590-B (Distributions from IRAs): https://www.irs.gov/publications/p590b
- SECURE 2.0 Act (RMD age change): https://www.congress.gov/bill/117th-congress/house-bill/2617
- IRS Topic 557 (Additional Tax on Early Distributions): https://www.irs.gov/taxtopics/tc557
- IRS Notice on Wash Sales (Pub 550): https://www.irs.gov/publications/p550
- Robinhood IRA Match: https://robinhood.com/us/en/about/ira/
