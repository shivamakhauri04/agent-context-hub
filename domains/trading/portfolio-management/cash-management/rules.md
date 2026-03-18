---
id: "trading/portfolio-management/cash-management/rules"
title: "Cash Management and Sweep Programs"
domain: "trading"
version: "1.0.0"
category: "portfolio-management"
tags:
  - cash-management
  - sweep
  - fdic
  - sipc
  - idle-cash
  - money-market
severity: "MEDIUM"
last_verified: "2026-03-17"
applies_to:
  - trading-agents
  - robo-advisors
  - portfolio-management-systems
related:
  - "trading/regulations/good-faith-violations/rules"
  - "trading/portfolio-management/goal-based-allocation/rules"
---

# Cash Management and Sweep Programs

## Summary

Cash management in brokerage accounts involves sweep programs (automatic movement of idle cash into interest-bearing vehicles), insurance coverage (FDIC and SIPC), settlement mechanics, and idle cash detection. Agents must understand the difference between FDIC and SIPC coverage, how sweep programs work, when cash is truly "available" vs. unsettled, and when idle cash signals a problem. Incorrect cash management exposes investors to uninsured deposits, missed yield on idle cash, good faith violations from using unsettled funds, and false confidence in insurance coverage that does not protect against market losses.

## The Problem

An agent that does not manage cash properly will: (1) allow investors to exceed FDIC coverage limits without warning, putting deposits at risk of loss in a bank failure, (2) leave large cash balances uninvested in non-emergency accounts, sacrificing yield, (3) conflate SIPC and FDIC coverage, telling investors their cash is "insured up to $500,000" when the cash limit is actually $250,000, (4) attempt to invest or sweep unsettled funds, causing good faith violations, (5) treat money market funds as risk-free when they can and have broken the buck, and (6) fail to distinguish between brokerage sweep programs and external high-yield savings accounts with different insurance and liquidity characteristics.

## Rules

1. **FDIC coverage: $250,000 per depositor, per insured bank, per ownership category.** The Federal Deposit Insurance Corporation insures bank deposits up to $250,000. Brokerage sweep programs that spread cash across multiple partner banks can provide coverage beyond $250,000 by distributing deposits. Example: Fidelity's FCASH sweeps to up to 5 banks = $1,250,000 FDIC coverage. Wealthfront Cash Account uses 4+ partner banks. The agent must track total deposits per bank across all accounts (including non-brokerage accounts at the same bank) to ensure the investor does not exceed $250,000 at any single bank.

2. **SIPC coverage: $500,000 total, of which $250,000 maximum for cash.** The Securities Investor Protection Corporation protects against broker-dealer failure (bankruptcy, fraud), NOT against market losses or bad investments. $500,000 total per customer per brokerage, with a $250,000 sub-limit on cash claims. If a broker fails with $400,000 of an investor's securities and $300,000 of cash, SIPC covers the full $400,000 in securities but only $250,000 of the $300,000 cash -- the investor loses $50,000. The agent must never represent SIPC as protection against investment losses.

3. **Sweep programs automatically move idle cash to interest-bearing vehicles.** Two main types: (a) bank deposit sweep -- cash moves to partner banks, earns interest, covered by FDIC, and (b) money market fund sweep -- cash moves to a money market mutual fund, earns yield, covered by SIPC (not FDIC). The agent should know which type the brokerage uses. Schwab uses bank deposit sweep (FDIC). Fidelity defaults to SPAXX money market (SIPC). Vanguard uses VMFXX money market. The type affects insurance, yield, and liquidity.

4. **Flag idle cash exceeding 5% of portfolio value in non-emergency accounts.** Cash sitting uninvested in a brokerage account earns sweep rates (often 0.01-0.50% at some brokers) while equities historically return ~10% annualized. For non-emergency goal accounts, cash above 5% of portfolio value likely indicates: missed DCA execution, paused recurring investments, undeployed proceeds from a sale, or cash from a dividend that was not reinvested. The agent should flag this and suggest action.

   | Portfolio Value | 5% Threshold | Action if Exceeded |
   |----------------|-------------|-------------------|
   | $10,000        | $500        | Flag if cash > $500 |
   | $50,000        | $2,500      | Flag if cash > $2,500 |
   | $100,000       | $5,000      | Flag if cash > $5,000 |
   | $500,000       | $25,000     | Flag if cash > $25,000 |

   Exception: accounts designated as emergency funds, accounts with pending large purchases, and accounts in drawdown phase (retirement income) should not be flagged.

5. **Settlement cash vs. available cash: unsettled funds cannot be swept or reinvested in cash accounts.** After selling a security, proceeds are unsettled for T+1 (US equities since May 2024). During this period, the cash appears in the account but is not yet "settled." In cash accounts (non-margin), using unsettled funds to buy and then selling that new purchase before the original sale settles is a good faith violation. The agent must distinguish between settled cash (available for sweep or new purchases) and unsettled cash (restricted). See `trading/regulations/good-faith-violations/rules` for the 3-strike enforcement.

6. **Money market funds are not guaranteed and can lose value.** Money market funds target a $1.00 net asset value (NAV) but are not FDIC-insured and can "break the buck" -- fall below $1.00 per share. This happened to the Reserve Primary Fund in September 2008, which fell to $0.97 NAV due to Lehman Brothers debt holdings, causing a $62.5 billion outflow and a broader money market panic. Government money market funds (investing only in Treasuries and repos) have never broken the buck and are considered safer. The agent should prefer government money market funds for cash allocation and never represent any money market fund as "guaranteed" or "risk-free."

7. **High-yield savings accounts vs. money market funds in brokerage.** These are different products with different characteristics:

   | Feature | HY Savings Account | Money Market Fund (Brokerage) |
   |---------|-------------------|------------------------------|
   | Insurance | FDIC ($250k per bank) | SIPC ($250k cash sub-limit) |
   | NAV stability | Guaranteed $1.00 | Targets $1.00, can break the buck |
   | Liquidity | 6 withdrawals/month (Reg D, though enforcement relaxed) | Same-day or T+1 |
   | Yield | Typically 4.0-5.0% APY (varies) | Typically 4.0-5.5% (varies) |
   | Tax reporting | 1099-INT | 1099-DIV |
   | Location | External bank | Inside brokerage account |

   The agent should help investors choose based on their priority: FDIC guarantee (choose HY savings), convenience and liquidity (choose money market in brokerage), or maximizing yield (compare current rates).

## Examples

### FDIC coverage calculator
```python
def calculate_fdic_coverage(
    sweep_banks: list[dict[str, float]],
    external_deposits: dict[str, float] | None = None,
) -> dict:
    """Calculate total FDIC coverage and identify uninsured amounts.

    Args:
        sweep_banks: List of {bank_name, deposit_amount} from sweep program
        external_deposits: Optional {bank_name: amount} for non-brokerage deposits
    """
    FDIC_LIMIT = 250_000
    external = external_deposits or {}

    results = []
    total_insured = 0.0
    total_uninsured = 0.0

    for bank in sweep_banks:
        name = bank["bank_name"]
        sweep_amount = bank["deposit_amount"]
        external_amount = external.get(name, 0)
        total_at_bank = sweep_amount + external_amount

        insured = min(total_at_bank, FDIC_LIMIT)
        uninsured = max(0, total_at_bank - FDIC_LIMIT)
        total_insured += insured
        total_uninsured += uninsured

        results.append({
            "bank": name,
            "sweep_deposit": sweep_amount,
            "external_deposit": external_amount,
            "total_at_bank": total_at_bank,
            "insured": insured,
            "uninsured": uninsured,
        })

    return {
        "banks": results,
        "total_insured": total_insured,
        "total_uninsured": total_uninsured,
        "fully_covered": total_uninsured == 0,
    }


# Example: $600k in sweep across 3 banks, $100k external at Bank A
# sweep_banks = [
#     {"bank_name": "Bank A", "deposit_amount": 200_000},
#     {"bank_name": "Bank B", "deposit_amount": 200_000},
#     {"bank_name": "Bank C", "deposit_amount": 200_000},
# ]
# external_deposits = {"Bank A": 100_000}
#
# Result:
# Bank A: $300k total ($200k sweep + $100k external) -> $250k insured, $50k UNINSURED
# Bank B: $200k total -> $200k insured, $0 uninsured
# Bank C: $200k total -> $200k insured, $0 uninsured
# Total: $650k insured, $50k uninsured -- NOT fully covered
```

### Idle cash detection
```python
def check_idle_cash(
    portfolio_value: float,
    cash_balance: float,
    goal_type: str,
    threshold_pct: float = 5.0,
) -> dict:
    """Check if portfolio has excessive idle cash."""
    exempt_goals = {"emergency", "drawdown", "pending_purchase"}

    if goal_type in exempt_goals:
        return {"flagged": False, "reason": f"Goal type '{goal_type}' is exempt"}

    cash_pct = (cash_balance / portfolio_value * 100) if portfolio_value > 0 else 0
    threshold_amount = portfolio_value * (threshold_pct / 100)

    if cash_balance > threshold_amount:
        return {
            "flagged": True,
            "cash_pct": round(cash_pct, 1),
            "cash_balance": cash_balance,
            "threshold_amount": threshold_amount,
            "excess_cash": round(cash_balance - threshold_amount, 2),
            "suggestion": "Consider investing excess cash or increasing DCA amount",
        }
    return {"flagged": False, "cash_pct": round(cash_pct, 1)}


# Example: $100,000 portfolio with $8,000 cash, goal = "retirement"
# Result: flagged=True, cash_pct=8.0%, excess=$3,000
#
# Example: $50,000 portfolio with $50,000 cash, goal = "emergency"
# Result: flagged=False, reason="Goal type 'emergency' is exempt"
```

## Agent Checklist

- [ ] Track total deposits per bank including external accounts for FDIC limits
- [ ] Never represent SIPC as protection against market or investment losses
- [ ] Know whether the brokerage uses bank deposit sweep (FDIC) or money market sweep (SIPC)
- [ ] Flag idle cash above 5% for non-emergency, non-drawdown accounts
- [ ] Distinguish settled vs. unsettled cash before investing or sweeping
- [ ] Use government money market funds over prime money market for cash reserves
- [ ] Never describe money market funds as "guaranteed" or "risk-free"
- [ ] Help investors compare HY savings vs. money market based on their priorities

## Structured Checks

```yaml
checks:
  - id: fdic_coverage_limit
    condition: "max_deposit_per_bank <= 250000"
    severity: high
    message: "Deposits at a single bank exceed $250,000 FDIC limit -- uninsured amount at risk"
  - id: idle_cash_threshold
    condition: "goal_type IN ('emergency', 'drawdown') OR cash_pct <= 5"
    severity: medium
    message: "Portfolio has more than 5% in idle cash -- consider investing or increasing DCA"
  - id: unsettled_cash_usage
    condition: "trade_uses_settled_cash == true"
    severity: high
    message: "Attempting to use unsettled funds -- risk of good faith violation"
```

## Sources

- FDIC: Deposit Insurance FAQs (coverage limits, per-bank rules)
- SIPC: What SIPC Protects (coverage limits, what is NOT covered)
- SEC: Money Market Fund Reform (2014, 2023 amendments)
- Reserve Primary Fund break-the-buck event (September 2008)
- Fidelity: Cash Management and Sweep Programs
- Schwab: Bank Deposit Sweep Program Disclosure
- Wealthfront: Cash Account and Partner Bank Coverage
- Federal Reserve Regulation D: Reserve Requirements (withdrawal limits)
