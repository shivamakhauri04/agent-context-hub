---
id: "trading/portfolio-management/esg-screening/rules"
title: "ESG/SRI Screening and Greenwashing Risks"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - esg
  - sri
  - greenwashing
  - fiduciary-duty
  - impact-investing
  - screening
severity: "HIGH"
last_verified: "2026-03-18"
applies_to:
  - trading-agents
  - robo-advisors
  - portfolio-management-systems
related:
  - "trading/portfolio-management/direct-indexing/rules"
  - "trading/portfolio-management/automated-rebalancing/rules"
  - "trading/regulations/suitability/rules"
---

# ESG/SRI Screening and Greenwashing Risks

## Summary

Environmental, Social, and Governance (ESG) and Socially Responsible Investing (SRI) portfolios are offered by Wealthfront, Betterment, and most major robo-advisors. ESG screening allows investors to align portfolios with values-based criteria -- excluding fossil fuels, weapons, tobacco, or companies with poor labor practices. However, ESG ratings are inconsistent across providers, "ESG" fund labels may be misleading (greenwashing), and exclusions impact portfolio diversification and tracking error. Agents must present ESG as a preference overlay, not a performance guarantee.

## The Problem

An agent that implements ESG screening without understanding the limitations will: (1) use ESG scores from a single provider without disclosing that other providers rate the same company differently, (2) recommend "ESG" funds that actually hold fossil fuel or weapons companies (greenwashing), (3) fail to quantify the impact of ESG exclusions on portfolio diversification and expected returns, (4) violate fiduciary duty by prioritizing ESG factors over financial materiality (DOL 2022 rule), (5) claim ESG investing always outperforms (or always underperforms) traditional investing, and (6) apply proxy voting assumptions that may not match the investor's actual preferences.

## Rules

1. **ESG rating inconsistency across providers is the norm, not the exception.** MSCI, Sustainalytics, and S&P Global ESG ratings for the same company frequently disagree. Tesla has an "AA" ESG rating from MSCI but a "High Risk" rating from Sustainalytics. A company rated "leader" by one agency may be rated "laggard" by another. The agent must disclose which ESG rating provider is being used and acknowledge that alternative ratings may differ significantly.

2. **Greenwashing risk: fund labels do not guarantee ESG compliance.** A fund labeled "ESG" or "Sustainable" may hold companies in fossil fuels, weapons, or private prisons. ESG fund methodologies vary widely -- some use best-in-class selection (top ESG scorers within each sector, including energy), others use exclusionary screening (remove entire sectors). The agent must examine the fund's actual holdings, not just its name or marketing label.

3. **ESG exclusions impact portfolio diversification and tracking error.** Excluding the energy sector (~4% of S&P 500), defense (~2%), and tobacco (~1%) reduces the investable universe and increases tracking error relative to broad benchmarks. For direct indexing, each exclusion category adds approximately 0.2-0.5% tracking error. The agent must quantify the cumulative tracking error from all applied exclusions and disclose it to the investor.

4. **Fiduciary duty constrains ESG application.** The DOL 2022 rule (for ERISA-governed retirement plans) permits consideration of ESG factors only when they are financially material -- meaning they affect risk and return. An agent managing 401(k) assets cannot exclude a sector purely on moral grounds if doing so is expected to harm returns. For non-ERISA accounts (taxable, IRA), investors have more latitude, but the agent should still disclose performance implications.

5. **Materiality varies by sector.** Carbon emissions are financially material for energy companies but less so for software companies. Water usage is material for agriculture and mining but not for financial services. The agent should apply sector-specific materiality frameworks rather than blanket ESG scores. SASB (Sustainability Accounting Standards Board) provides sector-specific materiality maps.

6. **Proxy voting alignment may differ from investor expectations.** Many ESG funds vote proxies on behalf of shareholders. The fund's proxy voting record may not align with the individual investor's values -- a fund might vote against a climate resolution that the investor supports. The agent should disclose that proxy voting is controlled by the fund manager, not the individual investor.

7. **Performance claims must be neutral.** Agents must not claim that ESG investing always outperforms or always underperforms traditional investing. Academic evidence is mixed and period-dependent. The agent should present ESG as a values-alignment tool with potential diversification trade-offs, not as an alpha generator or performance drag.

## Examples

### Example 1: Rating disagreement
Investor asks agent to screen for "high ESG" stocks. Using MSCI, Tesla qualifies (AA rating). Using Sustainalytics, Tesla is excluded (High Risk). The agent's recommendation changes entirely based on the chosen provider. Disclosure is mandatory.

### Example 2: Greenwashing detection
An "ESG Growth" ETF holds ExxonMobil in its top 20 positions because the fund uses a best-in-class methodology (Exxon is a top ESG scorer within the energy sector). An investor who wants to exclude fossil fuels would be misled by the fund name.

### Example 3: Fiduciary constraint
A 401(k) plan uses an ESG fund that excludes the energy sector. During an oil price surge, the fund underperforms its benchmark by 3%. Plan participants may have a fiduciary claim if the exclusion was not financially justified.

## Agent Checklist

- [ ] Disclose which ESG rating provider is used and that ratings differ across providers
- [ ] Verify actual fund holdings, not just fund name or marketing label
- [ ] Quantify tracking error impact from each ESG exclusion category
- [ ] Apply fiduciary duty constraints for ERISA accounts (401k plans)
- [ ] Use sector-specific materiality frameworks (SASB) rather than blanket scores
- [ ] Disclose proxy voting is controlled by fund manager, not individual investor
- [ ] Never claim ESG always outperforms or underperforms traditional investing

## Sources

- DOL 2022 Final Rule on ESG (ERISA): https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/resource-center/fact-sheets/final-rule-on-prudence-and-loyalty-in-selecting-plan-investments
- SASB Materiality Map: https://sasb.org/standards/materiality-map/
- SEC ESG Fund Naming Rule (2023): https://www.sec.gov/rules/final/2023/33-11238.pdf
- Berg, Koelbel, Rigobon (2022) "Aggregate Confusion: The Divergence of ESG Ratings"
