---
id: "trading/regulations/trust-accounts/rules"
title: "Trust Account Rules"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - trust
  - estate-planning
  - fiduciary
  - irrevocable
  - revocable
  - gst
  - estate-tax
severity: "HIGH"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - wealth-management-platforms
related:
  - "trading/regulations/ira-retirement/rules"
  - "trading/regulations/custodial-accounts/rules"
---

# Trust Account Rules

## Summary

Trust accounts require specialized compliance handling distinct from individual brokerage accounts. Key distinctions include fiduciary duty enforcement (self-dealing prohibition), estate tax exposure tracking against the federal exclusion amount ($13.61M per person in 2024, sunsetting to ~$7M in 2026), revocable vs irrevocable trust tax treatment, generation-skipping transfer tax (GSTT) exemption allocation, and sustainable distribution rate monitoring. An agent managing trust assets that ignores these constraints risks fiduciary breach, tax penalties, and trust corpus erosion.

## The Problem

Trust accounts are governed by the Uniform Trust Code and federal tax law. Agents that treat trust accounts like regular brokerage accounts will miss self-dealing violations (trustee transacting for personal benefit), fail to flag estate tax exposure when assets exceed the exclusion, allow unsustainable distribution rates that erode the trust corpus, and miss the critical distinction between revocable trusts (assets in grantor's taxable estate) and irrevocable trusts (assets removed from estate). The 2026 estate tax exclusion sunset makes this particularly urgent.

## Rules

1. **Self-dealing prohibition**: A trustee cannot transact for personal benefit from the trust. Any transaction where the trustee is on both sides must be flagged as a fiduciary breach.
2. **Estate tax exclusion tracking**: Trust assets exceeding the federal estate tax exclusion ($13.61M per person in 2024) trigger estate tax exposure. The exclusion is set to sunset to approximately $7M in 2026 under TCJA provisions.
3. **Revocable vs irrevocable distinction**: Revocable trust assets remain in the grantor's taxable estate and receive a step-up in basis at death. Irrevocable trust assets are removed from the estate but cannot be reclaimed by the grantor.
4. **Trustee-beneficiary conflict**: When the trustee of an irrevocable trust is also a beneficiary, distributions may be subject to IRS scrutiny as potential self-dealing.
5. **Generation-skipping transfer tax (GSTT)**: Transfers to beneficiaries more than one generation below the grantor trigger GSTT. The exemption ($13.61M in 2024) must be explicitly allocated and tracked.
6. **Sustainable distribution rate**: Annual distributions exceeding 7% of trust corpus risk depleting the trust over time. Academic and institutional guidance (e.g., endowment spending rules) suggest 4-5% as sustainable.
7. **Fiduciary investment standard**: Trustees must invest prudently under the Prudent Investor Rule -- diversification, risk-appropriate allocation, and consideration of the trust's purposes and beneficiary needs.

## Examples

### Self-dealing violation
```
Trustee buys a property from the trust at below-market value for personal use.
```
Result: Fiduciary breach. Beneficiaries can petition to void the transaction and remove the trustee.

### Estate tax exposure
```
Trust assets: $15,000,000
Estate tax exclusion: $13,610,000
Exposure: $1,390,000 at 40% federal rate = $556,000 estate tax liability
```
Action: Consider strategies to reduce exposure (charitable giving, GRAT, ILIT) before 2026 sunset.

### Unsustainable distribution
```
Trust corpus: $5,000,000
Annual distribution: $500,000 (10%)
Expected real return: 5-6%
```
Result: Trust corpus will be depleted within 15-20 years. Reduce to 4-5% or restructure.

## Agent Checklist

- [ ] Verify trust type (revocable vs irrevocable) before any transaction
- [ ] Check for self-dealing on every trustee-initiated transaction
- [ ] Compare trust assets against current estate tax exclusion amount
- [ ] Track GSTT exemption allocation for generation-skipping transfers
- [ ] Monitor annual distribution rate (flag >7%)
- [ ] For revocable trusts, remind that assets are in grantor's taxable estate
- [ ] Verify trustee-beneficiary relationship on irrevocable trusts

## Sources

- Uniform Trust Code (UTC), National Conference of Commissioners on Uniform State Laws
- IRC Section 2010 (Unified Credit Against Estate Tax)
- Tax Cuts and Jobs Act (TCJA) 2017, Section 11061 (Sunset Provision)
- IRC Section 2601-2664 (Generation-Skipping Transfer Tax)
- Restatement (Third) of Trusts: Prudent Investor Rule
- Robinhood "Take Flight" Event (March 2026): Trust account launch announcement
