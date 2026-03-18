---
id: "trading/portfolio-management/asset-location/rules"
title: "Tax-Coordinated Asset Location"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - asset-location
  - tax-efficiency
  - ira
  - roth
  - taxable
  - bonds
  - reits
severity: "HIGH"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - robo-advisors
  - portfolio-management-systems
related:
  - "trading/regulations/ira-retirement/rules"
  - "trading/regulations/tax-loss-harvesting/rules"
---

# Tax-Coordinated Asset Location

## Summary

Asset location is the strategy of placing investments in the most tax-efficient account type. Unlike asset allocation (what to own), asset location is about where to own it. Tax-inefficient assets (bonds, REITs, high-yield dividend stocks) belong in tax-advantaged accounts (Traditional IRA, 401k, Roth IRA). Tax-efficient assets (broad index funds, growth stocks, municipal bonds) belong in taxable accounts. Betterment estimates proper asset location adds 0.48% annual after-tax return. Agents that ignore asset location cost investors real money every year through unnecessary tax drag.

## The Problem

An agent that places assets without tax coordination will: (1) put REITs and high-yield bonds in taxable accounts where their distributions are taxed as ordinary income (up to 37% federal), (2) waste Roth IRA space on bonds that generate low growth when the entire point of Roth is tax-free growth, (3) put municipal bonds in an IRA where their tax exemption is worthless since IRA withdrawals are taxed as ordinary income anyway, (4) miss the opportunity to place the highest-growth assets in Roth accounts where gains are never taxed, and (5) fail to handle the common case where a single account type does not have enough space for all the assets that ideally belong there.

## Rules

1. **Tax-inefficient assets belong in tax-advantaged accounts (Traditional IRA, 401k).** Tax-inefficient assets generate income taxed at ordinary income rates. Placing them in tax-deferred accounts means no annual tax on distributions -- tax is only paid on withdrawal. Tax-inefficient assets include: taxable bonds (corporate, treasury), REITs (required to distribute 90% of income), high-yield dividend stocks, actively managed funds with high turnover, and TIPS (inflation adjustments are taxable annually).

2. **Tax-efficient assets belong in taxable accounts.** Tax-efficient assets generate little taxable income annually and benefit from favorable long-term capital gains rates (0%, 15%, or 20%) when sold. Tax-efficient assets include: broad market index funds (low turnover, minimal distributions), growth stocks (no dividends, gains deferred until sale), qualified dividend stocks (taxed at 15-20%, not ordinary rates), and tax-managed funds.

3. **Municipal bonds must always go in taxable accounts.** Municipal bond interest is exempt from federal income tax (and often state tax for in-state bonds). Placing munis in an IRA is a pure waste -- the tax exemption provides zero benefit inside a tax-advantaged account, and withdrawals from Traditional IRAs are taxed as ordinary income. A muni yielding 3.5% tax-free is equivalent to ~5.4% pre-tax for someone in the 35% bracket. That advantage vanishes inside an IRA.

4. **Roth IRA should hold the highest-growth assets.** Roth IRA contributions are after-tax, but all growth and withdrawals are tax-free. This makes Roth the ideal location for assets expected to appreciate the most: small-cap growth funds, emerging market equities, aggressive growth stocks. A $10,000 Roth investment that grows to $100,000 means $90,000 of tax-free gains. The same growth in a Traditional IRA means $90,000 taxed as ordinary income on withdrawal.

5. **Traditional IRA should hold income-generating assets.** Traditional IRA contributions may be tax-deductible, and all growth is tax-deferred. Income-generating assets (bonds, REITs, dividend stocks) benefit from deferral because their annual income is not taxed until withdrawal. Place in priority order: REITs (highest ordinary income), high-yield corporate bonds, TIPS, actively managed funds with high turnover.

6. **Priority table for limited account space.** Most investors do not have enough tax-advantaged space for all tax-inefficient assets. When account space is limited, prioritize placement in this order:

   **Traditional IRA / 401k (fill first with):**
   | Priority | Asset Type | Reason |
   |----------|-----------|--------|
   | 1 | REITs | Distributions taxed at ordinary income (up to 37%) |
   | 2 | High-yield corporate bonds | Interest taxed at ordinary income rates |
   | 3 | TIPS | Inflation adjustments taxed annually as phantom income |
   | 4 | Actively managed funds | High turnover generates short-term capital gains |
   | 5 | International stock funds | Foreign tax credit available only in taxable |

   **Roth IRA (fill with):**
   | Priority | Asset Type | Reason |
   |----------|-----------|--------|
   | 1 | Small-cap growth | Highest expected long-term appreciation |
   | 2 | Emerging markets | High growth potential, tax-free on withdrawal |
   | 3 | Aggressive growth stocks | Maximize tax-free compounding |

   **Taxable account (remainder):**
   | Priority | Asset Type | Reason |
   |----------|-----------|--------|
   | 1 | Municipal bonds | Tax-exempt interest wasted in tax-advantaged accounts |
   | 2 | Total market index funds | Low turnover, tax-efficient, eligible for LTCG rates |
   | 3 | Qualified dividend stocks | Dividends taxed at 15-20% (favorable rate) |
   | 4 | Tax-managed funds | Designed to minimize taxable distributions |
   | 5 | International funds (overflow) | Foreign tax credit offsets some tax drag |

   **Special case: international stock funds.** These are a placement dilemma. In a taxable account, investors can claim the Foreign Tax Credit for taxes paid to foreign governments (direct dollar-for-dollar credit). In a tax-advantaged account, this credit is lost. However, international funds with high distributions may still be better in tax-advantaged. Rule of thumb: if the foreign tax credit exceeds the tax drag from distributions, place in taxable.

## Examples

### Asset location engine
```python
from enum import Enum

class AccountType(Enum):
    TAXABLE = "taxable"
    TRADITIONAL_IRA = "traditional_ira"
    ROTH_IRA = "roth_ira"


# Priority: lower number = higher priority for that account type
ASSET_LOCATION_RULES: dict[str, dict[str, int]] = {
    # Asset type -> {account_type: priority}
    "reit":                {"traditional_ira": 1, "roth_ira": 99, "taxable": 99},
    "high_yield_bond":     {"traditional_ira": 2, "roth_ira": 99, "taxable": 99},
    "tips":                {"traditional_ira": 3, "roth_ira": 99, "taxable": 99},
    "active_managed_fund": {"traditional_ira": 4, "roth_ira": 99, "taxable": 99},
    "small_cap_growth":    {"roth_ira": 1, "traditional_ira": 99, "taxable": 5},
    "emerging_markets":    {"roth_ira": 2, "traditional_ira": 99, "taxable": 6},
    "muni_bond":           {"taxable": 1, "traditional_ira": 99, "roth_ira": 99},
    "total_market_index":  {"taxable": 2, "roth_ira": 4, "traditional_ira": 5},
    "qualified_dividend":  {"taxable": 3, "roth_ira": 5, "traditional_ira": 6},
}


def recommend_location(
    asset_type: str,
    available_accounts: list[str],
) -> str:
    """Return the best account type for a given asset."""
    rules = ASSET_LOCATION_RULES.get(asset_type)
    if not rules:
        return "taxable"  # Default: taxable for unknown assets

    best = min(
        available_accounts,
        key=lambda acct: rules.get(acct, 100),
    )
    return best


# Examples:
# recommend_location("reit", ["taxable", "traditional_ira", "roth_ira"])
#   -> "traditional_ira"  (priority 1)
#
# recommend_location("muni_bond", ["taxable", "traditional_ira"])
#   -> "taxable"  (priority 1, never waste muni tax exemption in IRA)
#
# recommend_location("small_cap_growth", ["taxable", "roth_ira"])
#   -> "roth_ira"  (priority 1, maximize tax-free growth)
```

### Tax drag calculation
```python
def annual_tax_drag(
    asset_value: float,
    yield_pct: float,
    tax_rate: float,
    account_type: str,
) -> float:
    """Calculate annual tax cost of holding an asset in the wrong account."""
    if account_type in ("traditional_ira", "roth_ira"):
        return 0.0  # No annual tax in tax-advantaged accounts
    annual_income = asset_value * (yield_pct / 100)
    return annual_income * tax_rate


# Example: $50,000 REIT yielding 8% in taxable account, 35% tax bracket
# Tax drag = $50,000 * 0.08 * 0.35 = $1,400/year
# Moving to Traditional IRA saves $1,400/year in tax drag.
#
# Example: $50,000 total market index yielding 1.5% in taxable, 15% LTCG rate
# Tax drag = $50,000 * 0.015 * 0.15 = $112.50/year
# This asset is already tax-efficient -- low priority to move.
```

## Agent Checklist

- [ ] Never place municipal bonds in tax-advantaged accounts
- [ ] Place REITs and high-yield bonds in Traditional IRA/401k first
- [ ] Place highest-growth assets (small-cap, emerging markets) in Roth IRA
- [ ] Place tax-efficient index funds and qualified dividend stocks in taxable accounts
- [ ] When tax-advantaged space is limited, follow the priority table
- [ ] Consider foreign tax credit eligibility when placing international funds
- [ ] Calculate tax drag to quantify the benefit of optimal placement
- [ ] Re-evaluate asset location when account balances or tax brackets change

## Structured Checks

```yaml
checks:
  - id: muni_bond_location
    condition: "asset_type != 'muni_bond' OR account_type == 'taxable'"
    severity: critical
    message: "Municipal bonds placed in tax-advantaged account -- tax exemption is wasted"
  - id: reit_location
    condition: "asset_type != 'reit' OR account_type != 'taxable'"
    severity: high
    message: "REIT in taxable account -- distributions taxed at ordinary income rates (up to 37%)"
  - id: roth_growth_assets
    condition: "account_type != 'roth_ira' OR expected_growth_rate >= median_growth_rate"
    severity: medium
    message: "Low-growth asset in Roth IRA -- Roth space should be reserved for highest-growth assets"
```

## Sources

- Betterment: Tax-Coordinated Portfolio White Paper (0.48% annual benefit estimate)
- Vanguard: Principles of Tax-Efficient Fund Placement
- Morningstar: Asset Location and Tax Efficiency
- Bogleheads Wiki: Tax-Efficient Fund Placement
- IRS Publication 550: Investment Income and Expenses
- IRS Publication 590-A: Contributions to Individual Retirement Arrangements (IRAs)
