---
id: "trading/regulations/suitability/rules"
title: "Reg BI and Suitability Obligations"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - suitability
  - reg-bi
  - finra-2111
  - kyc
  - risk-tolerance
  - investment-profile
severity: "HIGH"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - recommendation-engines
  - robo-advisors
related:
  - "trading/regulations/options-trading/rules"
  - "trading/regulations/margin-requirements/rules"
---

# Reg BI and Suitability Obligations

## Summary

FINRA Rule 2111 (Suitability) and SEC Regulation Best Interest (Reg BI) require that any investment recommendation must be suitable for the customer based on their investment profile. Reg BI imposes a higher "best interest" standard on broker-dealers. AI-generated recommendations are subject to the same obligations as human recommendations (FINRA Notice 24-09). Agents that suggest trades or strategies must verify suitability against the customer's risk tolerance, experience, financial situation, and investment objectives.

## The Problem

Trading agents that generate recommendations without checking customer suitability profiles face regulatory enforcement risk. Common failures: (1) recommending complex options strategies to novice investors, (2) suggesting speculative positions to retirees with conservative risk tolerance, (3) excessive trading (churning) that benefits the agent's turnover metrics but not the customer, (4) not maintaining or querying the customer investment profile before making recommendations. FINRA has flagged AI-driven recommendations as an emerging regulatory focus area in its 2025 oversight report.

## Rules

1. **Three Suitability Obligations (FINRA Rule 2111):**
   - **Reasonable-Basis Suitability**: The recommendation must be suitable for at least SOME investors. The agent must understand the product/strategy it is recommending.
   - **Customer-Specific Suitability**: The recommendation must be suitable for THIS specific customer based on their investment profile.
   - **Quantitative Suitability**: Even if each individual trade is suitable, the SERIES of recommendations must not be excessive (churning).

2. **Customer Investment Profile.** Before making any recommendation, the agent must have access to and consider:
   - Age and life stage
   - Annual income and liquid net worth
   - Tax status and filing situation
   - Investment objectives (capital preservation, income, growth, speculation)
   - Investment experience (years, product types traded)
   - Time horizon (short-term, medium-term, long-term)
   - Risk tolerance (conservative, moderate, aggressive, speculative)
   - Liquidity needs (how quickly funds may need to be accessed)

3. **Reg BI "Best Interest" Standard.** Since June 2020, SEC Regulation Best Interest requires broker-dealers to act in the customer's best interest when making recommendations. This is a HIGHER standard than suitability alone. It requires:
   - Disclosure of material facts about the recommendation
   - Exercise of reasonable diligence and care
   - Identification and mitigation of conflicts of interest
   - Compliance policies and procedures

4. **Quantitative Suitability Metrics.** FINRA uses two key metrics to detect excessive trading:
   - **Turnover Ratio**: Annualized ratio of total purchases to average account equity. A ratio above 6 is presumptively excessive.
   - **Cost-to-Equity Ratio**: Annualized ratio of total costs (commissions, fees, margin interest) to average account equity. A ratio above 20% is a red flag.

5. **AI-Generated Recommendations (FINRA Notice 24-09).** FINRA has explicitly stated that AI and algorithmic recommendations are subject to the same suitability and Reg BI obligations as human recommendations. Firms must:
   - Validate that AI models incorporate customer profile data
   - Monitor AI outputs for suitability compliance
   - Maintain records of how recommendations were generated
   - Have human oversight of AI recommendation systems

6. **Strategy Risk Levels.** For suitability matching, strategies should be classified by risk:

   | Risk Level | Strategies |
   |-----------|------------|
   | 1 (Conservative) | Treasury bonds, money market, covered calls on blue chips |
   | 2 (Moderate) | Diversified ETFs, investment-grade bonds, long stock |
   | 3 (Growth) | Individual stocks, sector ETFs, REITs |
   | 4 (Aggressive) | Small-cap stocks, leveraged ETFs, options spreads |
   | 5 (Speculative) | Penny stocks, naked options, crypto, meme stocks |

7. **Documentation Requirement.** Every recommendation must be logged with: the recommendation itself, the customer profile data consulted, the suitability analysis performed, and the rationale. This creates an audit trail for regulatory examination.

## Examples

### Suitability check before recommendation
```python
def check_suitability(
    strategy_risk: int,
    customer_risk_tolerance: int,
    strategy_complexity: int,
    customer_experience: int,
) -> list[str]:
    violations = []
    if strategy_risk > customer_risk_tolerance:
        violations.append(
            f"Risk mismatch: strategy risk {strategy_risk} "
            f"exceeds customer tolerance {customer_risk_tolerance}"
        )
    if strategy_complexity > customer_experience:
        violations.append(
            f"Experience mismatch: strategy complexity {strategy_complexity} "
            f"exceeds customer experience {customer_experience}"
        )
    return violations
```

### Quantitative suitability (churning detection)
```python
def check_churning(
    total_purchases_annual: float,
    total_costs_annual: float,
    avg_equity: float,
) -> list[str]:
    warnings = []
    if avg_equity > 0:
        turnover = total_purchases_annual / avg_equity
        cost_equity = total_costs_annual / avg_equity
        if turnover > 6:
            warnings.append(
                f"Excessive turnover: {turnover:.1f}x (threshold: 6x)"
            )
        if cost_equity > 0.20:
            warnings.append(
                f"High cost-to-equity: {cost_equity:.1%} (threshold: 20%)"
            )
    return warnings
```

### Unsuitable recommendation scenario
```
Customer profile:
  Age: 68, retired
  Risk tolerance: Conservative (1)
  Experience: 2 years, only mutual funds
  Objective: Capital preservation
  Time horizon: Short-term (< 2 years)

Agent recommends: Sell naked puts on TSLA
  Strategy risk: 5 (Speculative)
  Strategy complexity: 4 (Advanced)

SUITABILITY VIOLATIONS:
  1. Risk mismatch: speculative strategy for conservative investor
  2. Experience mismatch: naked options require advanced experience
  3. Time horizon mismatch: short-term horizon incompatible with margin risk
```

## Agent Checklist

- [ ] Query customer investment profile before ANY recommendation
- [ ] Map each strategy to a risk level and complexity level
- [ ] Compare strategy risk against customer risk tolerance — reject if mismatch
- [ ] Compare strategy complexity against customer experience — reject if mismatch
- [ ] Track turnover ratio and cost-to-equity ratio for quantitative suitability
- [ ] Log every recommendation with suitability analysis for audit trail
- [ ] Flag when customer profile is missing or incomplete — do not recommend without it
- [ ] Periodically re-verify customer profile (profiles can change)

## Structured Checks

```yaml
checks:
  - id: suitability_risk_match
    condition: "strategy_risk_level <= customer_risk_tolerance"
    severity: high
    message: "Strategy risk exceeds customer risk tolerance"
  - id: suitability_experience_check
    condition: "strategy_complexity <= customer_experience_level"
    severity: high
    message: "Strategy complexity exceeds customer experience level"
```

## Sources

- FINRA Rule 2111 (Suitability): https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111
- SEC Regulation Best Interest: https://www.sec.gov/regulation-best-interest
- FINRA Notice 24-09 (AI in Securities Industry): https://www.finra.org/rules-guidance/notices/24-09
- FINRA 2025 Annual Regulatory Oversight Report: https://www.finra.org/rules-guidance/guidance/reports/2025-annual-regulatory-oversight-report
- FINRA Regulatory Notice 12-25 (Suitability FAQ): https://www.finra.org/rules-guidance/notices/12-25
