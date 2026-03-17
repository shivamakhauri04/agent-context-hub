---
id: "trading/regulations/crypto-trading/rules"
title: "Crypto Trading Rules"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - crypto
  - bitcoin
  - ethereum
  - digital-assets
  - no-sipc
  - tax
  - staking
severity: "CRITICAL"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - crypto-trading-bots
related:
  - "trading/regulations/wash-sale/rules"
  - "trading/market-structure/trading-hours/reference"
---

# Crypto Trading Rules

## Summary

Cryptocurrency trading operates under a fundamentally different regulatory framework than equities. There is no SIPC or FDIC insurance, no Pattern Day Trader rule, no NBBO price guarantee, and the IRS treats crypto as property (not currency). Starting in 2025, the wash sale rule extends to digital assets. An agent that applies equity trading rules to crypto will produce incorrect tax calculations, miss insurance gaps, and mishandle execution. Every assumption from equities must be re-examined for crypto.

## The Problem

An agent built for equity trading that also handles crypto will get nearly everything wrong: (1) applying PDT restrictions when there are none, (2) assuming SIPC protection when crypto has none, (3) ignoring that every trade — including crypto-to-crypto swaps — is a taxable event, (4) not applying wash sale rules starting 2025, (5) assuming T+2 settlement when crypto settles differently, (6) expecting NBBO pricing when crypto has no best-execution guarantee. These are not edge cases — they are fundamental differences that affect every transaction.

## Rules

1. **Crypto is NOT SIPC or FDIC insured.** Unlike equities (SIPC up to $500k) or bank deposits (FDIC up to $250k), crypto held at an exchange has zero federal insurance. If the exchange fails, customer assets may be lost entirely (see FTX, Celsius, Voyager bankruptcies). Agents must disclose this risk and consider it in position sizing.

2. **No Pattern Day Trader rule for crypto.** The PDT rule (FINRA Rule 4210) applies only to margin accounts trading securities. Crypto is classified as property, not securities (for most tokens). Day trade freely without count restrictions. However, this does NOT mean crypto margin trading is unregulated — exchanges set their own rules.

3. **IRS treats crypto as property (IRC Section 1001).** Every disposal — sale, trade, swap, spend, gift (over $17k) — is a taxable event. This includes: crypto-to-crypto trades (e.g., BTC to ETH), using crypto to buy goods, receiving crypto as payment (ordinary income at FMV), and airdrops/forks (ordinary income when received). FIFO is the default cost basis method unless specifically elected otherwise.

4. **Wash sale rule extends to crypto starting 2025.** Before 2025, crypto was exempt from wash sale rules (IRC Section 1091 applied only to "stock or securities"). Starting 2025, selling crypto at a loss and repurchasing the same crypto within 30 days triggers wash sale treatment — the loss is disallowed and added to the replacement cost basis. Agents must implement 30-day window tracking for crypto trades.

5. **24/7/365 trading — no market hours.** Crypto markets never close. There are no opening/closing bells, no trading halts (at the protocol level), and no holidays. Liquidity varies significantly by time of day — lowest during Asian night hours (roughly 02:00-06:00 UTC). Weekend liquidity is typically 30-50% lower than weekday peaks.

6. **Settlement is near-instant but varies.** Unlike equities (T+2), crypto settlement depends on blockchain confirmation. Bitcoin: ~10 minutes (1 confirmation), 60 minutes (6 confirmations for high-value). Ethereum: ~12 seconds (1 block), ~5 minutes (finality). Exchange-internal transfers settle instantly. On-chain transfers incur network fees.

7. **No NBBO — prices vary across exchanges.** There is no National Best Bid and Offer for crypto. Prices can differ 0.1-2% across exchanges (more for illiquid tokens). Arbitrage bots partially equalize prices but spreads persist. Agents should not assume consistent pricing across venues.

8. **Staking rewards are taxable as ordinary income.** Staking rewards (proof-of-stake) are taxed as ordinary income at fair market value when received. This creates a tax liability even without selling. The cost basis for future sale is the FMV at time of receipt. Some staking rewards are paid in-kind (same token) and some in different tokens.

9. **Wallet-to-wallet transfers are NOT taxable events.** Moving crypto between your own wallets (including exchange to hardware wallet) is not a disposal and not taxable. However, network transaction fees (gas fees) are not deductible as investment expenses under current IRS guidance (post-TCJA).

10. **Slippage is significantly higher for illiquid tokens.** Market orders on low-cap tokens can experience 5-20% slippage. Limit orders are strongly recommended. Liquidity pools (DeFi) have additional slippage from automated market maker curves. Agents should check order book depth before placing large orders.

## Examples

### Tax lot tracking for crypto
```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class CryptoTaxLot:
    """A single purchase lot for cost basis tracking."""
    symbol: str
    quantity: Decimal
    cost_basis_per_unit: Decimal
    acquired_date: datetime

    @property
    def total_cost(self) -> Decimal:
        return self.quantity * self.cost_basis_per_unit

    def is_long_term(self, disposal_date: datetime) -> bool:
        """Held > 1 year qualifies for long-term capital gains rate."""
        return (disposal_date - self.acquired_date).days > 365
```

### Wash sale check for crypto (2025+)
```
Scenario (2025):
Day 1:  Sell 1.0 BTC at loss (-$5,000)
Day 20: Buy 0.5 BTC (within 30-day window)

Result: 50% of loss ($2,500) disallowed — wash sale triggered.
Remaining $2,500 loss is deductible.
$2,500 added to cost basis of new 0.5 BTC.

Before 2025: Full $5,000 loss deductible (no wash sale for crypto).
```

### 24/7 liquidity variation
```
Typical BTC/USD liquidity (approximate order book depth):
  US market hours (14:30-21:00 UTC):   HIGH  — tightest spreads
  European overlap (08:00-14:30 UTC):  MEDIUM
  Asian session (00:00-08:00 UTC):     MEDIUM
  Weekend / off-hours:                 LOW   — wider spreads, more slippage
```

## Agent Checklist

- [ ] Never assume SIPC/FDIC protection for crypto holdings
- [ ] Do not apply PDT restrictions to crypto trades
- [ ] Track every crypto disposal as a taxable event (including crypto-to-crypto)
- [ ] For 2025+: implement wash sale 30-day window tracking for crypto
- [ ] Use FIFO cost basis method unless user specifies otherwise
- [ ] Account for staking rewards as ordinary income at FMV when received
- [ ] Check liquidity / order book depth before large market orders
- [ ] Do not assume consistent pricing across exchanges
- [ ] Handle 24/7 market hours — no session boundaries

## Structured Checks

```yaml
checks:
  - id: crypto_not_sipc_protected
    condition: "asset_class != 'crypto' OR sipc_awareness == 'true'"
    severity: critical
    message: "Crypto assets are NOT SIPC or FDIC insured"
  - id: crypto_wash_sale_2025
    condition: "asset_class != 'crypto' OR trade_year < 2025 OR wash_sale_checked == 'true'"
    severity: high
    message: "Crypto wash sale rule applies starting 2025 — check 30-day window"
```

## Sources

- IRS Notice 2014-21 (Crypto as property): https://www.irs.gov/irb/2014-16_IRB#NOT-2014-21
- IRS Rev. Rul. 2019-24 (Airdrops, forks): https://www.irs.gov/pub/irs-drop/rr-19-24.pdf
- IRC Section 1091 (Wash sales, extended to crypto 2025): https://www.law.cornell.edu/uscode/text/26/1091
- IRS Publication 544 (Sales and Dispositions of Assets): https://www.irs.gov/publications/p544
- FINRA Crypto Asset Communication Rules: https://www.finra.org/rules-guidance/key-topics/crypto-assets
