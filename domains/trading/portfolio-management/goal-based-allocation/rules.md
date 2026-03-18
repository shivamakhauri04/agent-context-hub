---
id: "trading/portfolio-management/goal-based-allocation/rules"
title: "Goal-Based Portfolio Allocation"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - goal-based
  - allocation
  - risk-score
  - glide-path
  - robo-advisor
severity: "HIGH"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - robo-advisors
  - portfolio-management-systems
related:
  - "trading/portfolio-management/automated-rebalancing/rules"
  - "trading/regulations/suitability/rules"
---

# Goal-Based Portfolio Allocation

## Summary

Goal-based allocation assigns a distinct asset allocation to each investor goal (retirement, emergency fund, house down payment, education, general investing). Each goal has its own time horizon, risk tolerance, and liquidity needs, which determine the equity/bond/cash mix. Robo-advisors (Betterment, Wealthfront) and modern portfolio management systems treat goals as separate buckets with independent allocations. Agents that blend goals into a single allocation will mismatch risk to time horizon, expose short-term goals to equity drawdowns, or under-invest long-term goals in growth assets.

## The Problem

An agent that applies a single portfolio allocation across all goals will: (1) expose emergency funds to equity risk, violating the fundamental requirement that emergency reserves be immediately accessible and stable, (2) over-allocate bonds for a 30-year retirement goal, sacrificing decades of compounding growth, (3) put a 2-year house down payment fund into 80% equities, risking a 30%+ drawdown right before the purchase, (4) fail to adjust allocations as goal target dates approach (no glide path), and (5) create tax and rebalancing chaos by mixing goal-specific trades in a single account without logical separation.

## Rules

1. **Goal type determines base allocation.** Each goal type has a default allocation strategy based on its nature and typical time horizon. Retirement: age-based equity allocation (common rule: equity % = 110 - age, or more conservative 100 - age). Emergency fund: 100% cash or money market, no exceptions. House down payment: horizon-dependent (see rule 3). Education (529): glide-path based on child's age. General investing: risk-score based (see rule 4).

2. **Emergency fund must be 100% cash or money market.** Emergency funds exist for immediate, unplanned access. They must never contain equities, bonds, or any asset with principal risk or settlement delays. Money market funds are acceptable (same-day liquidity, near-zero volatility). High-yield savings accounts are also acceptable. No exceptions -- even "conservative" bond funds lost 13% in 2022.

3. **Short-term goals (<3 years) must limit equity exposure.** Goals with a time horizon under 3 years should hold at least 70% in bonds and cash, with a maximum of 30% in equities. A 20% equity drawdown on a $60,000 house down payment fund means $12,000 lost with no time to recover. Specific breakdown by horizon:
   - < 1 year: 100% cash/money market
   - 1-2 years: 80-90% bonds/cash, 10-20% equities
   - 2-3 years: 70% bonds/cash, 30% equities

4. **Risk score (1-10) maps to equity/bond ratio for general investing goals.** When the goal is general wealth building without a fixed target date, use the investor's risk score to determine allocation:

   | Risk Score | Equities | Bonds | Cash |
   |------------|----------|-------|------|
   | 1          | 10%      | 70%   | 20%  |
   | 2          | 20%      | 65%   | 15%  |
   | 3          | 30%      | 60%   | 10%  |
   | 4          | 40%      | 55%   | 5%   |
   | 5          | 50%      | 47%   | 3%   |
   | 6          | 60%      | 38%   | 2%   |
   | 7          | 70%      | 28%   | 2%   |
   | 8          | 80%      | 18%   | 2%   |
   | 9          | 90%      | 9%    | 1%   |
   | 10         | 95%      | 5%    | 0%   |

5. **Glide path: reduce equity by 1-2% per year as target date approaches.** For goals with a known target date (retirement, education, house purchase), the allocation should gradually shift from equities to bonds/cash as the date nears. Start aggressive, end conservative. Example: retirement target in 30 years starts at 90% equity, shifts to ~40% equity at retirement. Education fund for a newborn starts at 80% equity, shifts to 20% equity by age 17. The glide path should be linear or follow a target-date fund curve (aggressive early, accelerating shift in final 10 years).

6. **Multiple goals require separate buckets.** Each goal must have its own allocation tracked independently. Never blend allocations across goals. A single brokerage account can hold multiple logical goals using sub-account tagging or virtual portfolios. Rebalancing one goal must not affect another goal's allocation. Withdrawals from one goal must not trigger rebalancing in another.

7. **Rebalancing frequency should match goal horizon.** Long-term goals (10+ years): annual rebalancing or drift-threshold-based (5% absolute drift). Medium-term goals (3-10 years): semi-annual rebalancing. Short-term goals (<3 years): quarterly rebalancing or tighter drift thresholds (3% absolute drift). Emergency funds: no rebalancing needed (100% cash).

## Examples

### Goal-based allocation engine
```python
from datetime import date

RISK_SCORE_EQUITY_MAP = {
    1: 0.10, 2: 0.20, 3: 0.30, 4: 0.40, 5: 0.50,
    6: 0.60, 7: 0.70, 8: 0.80, 9: 0.90, 10: 0.95,
}


def get_goal_allocation(
    goal_type: str,
    years_to_target: float | None = None,
    age: int | None = None,
    risk_score: int | None = None,
) -> dict[str, float]:
    """Return target allocation for a goal as {equities, bonds, cash}."""

    if goal_type == "emergency":
        return {"equities": 0.0, "bonds": 0.0, "cash": 1.0}

    if goal_type == "retirement" and age is not None:
        equity_pct = max(0.20, min(0.90, (110 - age) / 100))
        bond_pct = round(1.0 - equity_pct - 0.02, 2)
        return {"equities": equity_pct, "bonds": bond_pct, "cash": 0.02}

    if goal_type in ("house_downpayment", "education") and years_to_target is not None:
        if years_to_target < 1:
            return {"equities": 0.0, "bonds": 0.0, "cash": 1.0}
        elif years_to_target < 3:
            equity_pct = min(0.30, years_to_target * 0.15)
            return {"equities": equity_pct, "bonds": 0.70, "cash": round(1.0 - equity_pct - 0.70, 2)}
        else:
            # Glide path: start higher, reduce as target approaches
            equity_pct = min(0.80, 0.30 + (years_to_target - 3) * 0.05)
            return {"equities": equity_pct, "bonds": round(1.0 - equity_pct - 0.02, 2), "cash": 0.02}

    if goal_type == "general" and risk_score is not None:
        equity_pct = RISK_SCORE_EQUITY_MAP.get(risk_score, 0.50)
        bond_pct = round(1.0 - equity_pct - 0.02, 2)
        return {"equities": equity_pct, "bonds": max(0.0, bond_pct), "cash": 0.02}

    raise ValueError(f"Cannot determine allocation for goal_type={goal_type}")


# Examples:
# Emergency fund:            {equities: 0%, bonds: 0%, cash: 100%}
# Retirement, age 30:        {equities: 80%, bonds: 18%, cash: 2%}
# Retirement, age 60:        {equities: 50%, bonds: 48%, cash: 2%}
# House down payment, 2yr:   {equities: 30%, bonds: 70%, cash: 0%}
# House down payment, 8yr:   {equities: 55%, bonds: 43%, cash: 2%}
# Education, 15yr to target: {equities: 80%, bonds: 18%, cash: 2%}
# General, risk score 7:     {equities: 70%, bonds: 28%, cash: 2%}
```

### Multi-goal portfolio summary
```python
def portfolio_summary(goals: list[dict]) -> dict:
    """Summarize total portfolio across all goal buckets."""
    total_value = sum(g["value_usd"] for g in goals)
    weighted_equity = sum(
        g["value_usd"] * g["allocation"]["equities"] for g in goals
    ) / total_value
    weighted_bonds = sum(
        g["value_usd"] * g["allocation"]["bonds"] for g in goals
    ) / total_value
    weighted_cash = sum(
        g["value_usd"] * g["allocation"]["cash"] for g in goals
    ) / total_value
    return {
        "total_value_usd": total_value,
        "blended_equities_pct": round(weighted_equity * 100, 1),
        "blended_bonds_pct": round(weighted_bonds * 100, 1),
        "blended_cash_pct": round(weighted_cash * 100, 1),
    }

# Example:
# Goal 1: Retirement, $200,000, {equities: 80%, bonds: 18%, cash: 2%}
# Goal 2: Emergency,  $15,000,  {equities: 0%, bonds: 0%, cash: 100%}
# Goal 3: House,      $40,000,  {equities: 30%, bonds: 70%, cash: 0%}
# Blended: total $255,000, equities 51.4%, bonds 25.1%, cash 23.5%
# NOTE: blended view is informational only -- do NOT rebalance to blended targets.
```

## Agent Checklist

- [ ] Classify each goal by type before assigning allocation
- [ ] Enforce 100% cash for emergency fund goals with no override
- [ ] Cap equities at 30% for goals with <3 year horizon
- [ ] Apply risk score mapping for general investing goals
- [ ] Implement glide path that reduces equity as target date approaches
- [ ] Maintain separate allocation buckets per goal -- never blend
- [ ] Set rebalancing frequency appropriate to each goal's horizon
- [ ] Validate that goal type and required parameters (age, horizon, risk score) are provided

## Structured Checks

```yaml
checks:
  - id: emergency_fund_allocation
    condition: "goal_type != 'emergency' OR (equities_pct == 0 AND bonds_pct == 0)"
    severity: critical
    message: "Emergency fund must be 100% cash/money market -- equities and bonds are not permitted"
  - id: short_term_equity_limit
    condition: "years_to_target >= 3 OR equities_pct <= 30"
    severity: high
    message: "Short-term goal (<3 years) has more than 30% equities -- excessive risk for time horizon"
  - id: goal_bucket_separation
    condition: "goals_share_allocation == false"
    severity: high
    message: "Multiple goals are sharing a single allocation -- each goal must have its own bucket"
```

## Sources

- Betterment: Goal-Based Investing Methodology
- Wealthfront: Path Financial Planning Engine
- Vanguard Target Retirement Funds: Glide Path Methodology
- CFP Board: Financial Planning Competency Handbook (Goal-Based Planning)
- Morningstar: The Role of Time Horizon in Asset Allocation
- FINRA Investor Education: Setting Investment Goals
