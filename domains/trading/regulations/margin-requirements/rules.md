---
id: "trading/regulations/margin-requirements/rules"
title: "Margin Requirements and Reg T"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - margin
  - reg-t
  - finra-4210
  - maintenance
  - margin-call
  - liquidation
severity: "CRITICAL"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - risk-management-systems
related:
  - "trading/regulations/pdt-rule/rules"
  - "trading/regulations/options-trading/rules"
---

# Margin Requirements and Reg T

## Summary

Margin accounts allow investors to borrow from their broker to buy securities. Federal Reserve Regulation T sets the initial margin at 50% for equities. FINRA Rule 4210 sets the maintenance margin minimum at 25%. Brokers impose "house requirements" of 30-40% or higher. When equity falls below maintenance margin, a margin call is issued. Brokers can liquidate ANY position WITHOUT notice or waiting if they choose. Agents must continuously monitor margin ratio and react to margin calls immediately.

## The Problem

Trading agents that use margin without monitoring margin ratio will eventually face forced liquidation. Common failures: (1) not calculating margin ratio after each trade, (2) assuming the broker will wait for you to deposit funds (they won't — forced liquidation can happen immediately), (3) ignoring concentrated position requirements where a single stock >50% of the portfolio triggers higher margin, (4) not understanding that market drops reduce equity and can trigger margin calls even without new trades.

## Rules

1. **Initial Margin (Reg T = 50%).** When opening a new position on margin, you must deposit at least 50% of the purchase price. To buy $10,000 of stock, you need $5,000 in equity. The remaining $5,000 is borrowed from the broker.

2. **Maintenance Margin (FINRA minimum = 25%).** After a position is established, equity must remain at or above 25% of the total market value. The margin ratio formula:

   ```
   margin_ratio = equity / market_value
   equity = market_value - margin_loan
   ```

   If margin_ratio drops below 25%, a margin call is triggered.

3. **House Requirements (30-40%+ typical).** Most brokers set their own maintenance margin above the FINRA 25% minimum. Common house requirements: 30% for diversified portfolios, 40% for volatile stocks, 50-100% for concentrated positions or penny stocks.

4. **Margin Calls.** When equity drops below maintenance margin:
   - Broker issues a margin call requiring deposit of additional funds or sale of securities
   - Deadline is typically 2-5 business days, BUT the broker can liquidate immediately
   - The broker chooses WHICH positions to liquidate — not the customer
   - Liquidation often happens at the worst possible time (market drops)
   - The customer owes any remaining deficit after liquidation

5. **Day Trading Buying Power.** For accounts flagged as Pattern Day Traders (PDT), day trading buying power is 4x maintenance margin excess. For example, with $30,000 equity and $25,000 minimum: excess = $5,000, day trading buying power = $20,000. This resets daily.

6. **Concentrated Positions.** When a single security represents more than 40-50% of the portfolio's market value, brokers typically increase margin requirements to 50-70% for that position. Some brokers require 100% margin (no leverage) for positions over 70% concentration.

7. **Short Selling Margin.** Short selling requires 150% margin at initiation (100% proceeds + 50% deposit). Maintenance margin for short positions is typically 130% of current market value. If the stock rises, margin requirements increase proportionally.

8. **Margin Interest.** Borrowed funds accrue interest daily. Rates vary by broker and loan amount (typically 5-13% annually). Interest compounds and reduces account equity over time, potentially triggering margin calls even in flat markets.

9. **Margin and Options.** Certain options strategies have special margin requirements: covered calls reduce margin on the underlying, spreads require margin equal to the max loss, naked options have their own margin formulas based on the underlying price and strike.

## Examples

### Margin ratio calculation
```python
def calculate_margin_ratio(
    market_value: float,
    margin_loan: float,
) -> float:
    if market_value <= 0:
        return 0.0
    equity = market_value - margin_loan
    return equity / market_value

# Example: $100k portfolio with $60k loan
# equity = $40k, ratio = 40/100 = 0.40 (healthy)
# Stock drops 30%: market_value = $70k, equity = $10k
# ratio = 10/70 = 0.143 (BELOW 25% — margin call!)
```

### Margin call scenario
```
Day 1: Buy $100,000 of NVDA on margin
  Market value: $100,000
  Margin loan: $50,000 (50% initial margin)
  Equity: $50,000
  Margin ratio: 50% (healthy)

Day 5: NVDA drops 35%
  Market value: $65,000
  Margin loan: $50,000 (unchanged)
  Equity: $15,000
  Margin ratio: 23.1% (BELOW 25% — MARGIN CALL)

Broker demands: deposit ~$1,250 to restore 25%
  OR broker liquidates your NVDA at market price
  Broker may liquidate without waiting for deposit
```

### Concentrated position check
```python
def check_concentration(positions: list[dict], market_value: float) -> list[str]:
    warnings = []
    for pos in positions:
        pos_value = pos["quantity"] * pos["current_price"]
        concentration = pos_value / market_value if market_value > 0 else 0
        if concentration > 0.50:
            warnings.append(
                f"{pos['symbol']}: {concentration:.0%} of portfolio — "
                f"higher margin requirement likely"
            )
    return warnings
```

## Agent Checklist

- [ ] Calculate margin ratio after every trade and at start of each session
- [ ] Set alerts at house requirement + 5% buffer (e.g., alert at 35% if house = 30%)
- [ ] Never assume broker will wait for margin call deposit — prepare for immediate liquidation
- [ ] Track concentrated positions and apply higher margin requirements
- [ ] Account for margin interest when calculating long-term holding costs
- [ ] For short positions, use 150% initial / 130% maintenance calculations
- [ ] Monitor day trading buying power separately from overnight margin
- [ ] Log margin ratio history for risk auditing

## Structured Checks

```yaml
checks:
  - id: margin_maintenance_check
    condition: "margin_ratio >= 0.25 OR account_type == 'cash'"
    severity: critical
    message: "Account below FINRA 25% maintenance margin — margin call imminent"
  - id: margin_initial_check
    condition: "margin_ratio >= 0.50 OR account_type == 'cash' OR is_existing_position == 'true'"
    severity: high
    message: "New position requires 50% initial margin (Reg T)"
  - id: margin_house_requirement
    condition: "margin_ratio >= house_margin_requirement OR account_type == 'cash'"
    severity: high
    message: "Account below broker house margin requirement"
```

## Sources

- Federal Reserve Regulation T: https://www.ecfr.gov/current/title-12/chapter-II/subchapter-A/part-220
- FINRA Rule 4210 (Margin Requirements): https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210
- FINRA Margin Account Guide: https://www.finra.org/investors/investing/investing-basics/understanding-margin-accounts
- SEC Investor Bulletin on Margin: https://www.sec.gov/oiea/investor-alerts-and-bulletins/ib_marginaccount
- FINRA 2025 Annual Regulatory Oversight Report: https://www.finra.org/rules-guidance/guidance/reports/2025-annual-regulatory-oversight-report
