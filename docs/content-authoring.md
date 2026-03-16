# Content Authoring Guide

How to write content documents that AI agents can reliably use.

## Frontmatter Reference

Every content document begins with YAML frontmatter enclosed in `---` delimiters. The following fields are validated against `schemas/content-frontmatter.json`.

### Required fields

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | string | Unique content identifier matching the file path | `trading/regulations/pdt-rule/rules` |
| `title` | string | Human-readable title (min 5 characters) | `Pattern Day Trader (PDT) Rule` |
| `domain` | string | Parent domain name | `trading` |
| `version` | string | Semantic version | `1.0.0` |
| `category` | string | Category within the domain | `regulations` |
| `tags` | list[string] | Searchable tags (min 1) | `[pdt, day-trading, finra]` |
| `severity` | string | Impact level: CRITICAL, HIGH, MEDIUM, LOW, or INFO | `CRITICAL` |
| `last_verified` | string | Date content was last fact-checked (YYYY-MM-DD) | `2026-03-01` |

### Optional fields

| Field | Type | Description | Example |
|---|---|---|---|
| `applies_to` | list[string] | Types of agents this applies to | `[trading-agents, portfolio-systems]` |
| `related` | list[string] | Content IDs of related documents | `[trading/broker-apis/alpaca/quirks]` |

### ID format

The `id` field must match the pattern `^[a-z0-9-]+(/[a-z0-9-]+)*$`. It should mirror the file path relative to `domains/`:

```
File:  domains/trading/regulations/pdt-rule/rules.md
ID:    trading/regulations/pdt-rule/rules
```

## Standard Sections

Every content document should include the following sections in order. This consistency allows agents to reliably parse and extract information.

### Summary

One paragraph. State what this document covers, why it matters, and the key constraint or rule. An agent should be able to read only this paragraph and understand whether the document is relevant.

```markdown
## Summary

The Pattern Day Trader rule is a FINRA regulation (Rule 4210) that restricts
accounts with less than $25,000 in equity from making 4 or more day trades
within a rolling 5-business-day window when using a margin account. Violation
triggers a 90-day trading restriction or a margin call.
```

### The Problem

One to two paragraphs. Describe what goes wrong when an agent does not have this knowledge. Use concrete examples -- real tickers, real dates, real numbers. This section justifies the document's existence.

```markdown
## The Problem

A trading agent executing a momentum strategy on a $10,000 margin account will
commonly make 4+ round trips in a single week. Without PDT awareness, the agent
triggers a FINRA violation on the 4th day trade, resulting in a 90-day trading
freeze on the account. The agent continues to submit orders that are silently
rejected, and the user discovers the problem only after checking their broker
dashboard days later.
```

### Rules

Numbered list of concrete, actionable directives. Each rule should be unambiguous and testable. Avoid vague guidance like "be careful" -- instead state the exact constraint.

```markdown
## Rules

1. Count day trades in a rolling 5-business-day window, not calendar days.
2. A day trade is defined as opening and closing the same position on the same
   trading day, regardless of the number of shares.
3. If the account equity is below $25,000 and the account type is margin,
   limit day trades to 3 within the rolling window.
4. If the account type is cash, the PDT rule does not apply, but settlement
   rules (T+2) still restrict rapid trading.
5. Options count as day trades if opened and closed on the same day.
```

### Examples

Real-world scenarios with actual data. Use specific tickers, dates, prices, and quantities. Show both the correct and incorrect behavior.

```markdown
## Examples

### Example 1: PDT violation on 4th trade

Account: $15,000 equity, margin type
- Monday: Buy 100 AAPL at $150, sell at $152 (day trade #1)
- Tuesday: Buy 50 TSLA at $200, sell at $205 (day trade #2)
- Wednesday: Buy 200 NVDA at $400, sell at $410 (day trade #3)
- Thursday: Buy 100 AAPL at $153, sell at $155 (day trade #4 -- VIOLATION)

Result: Account flagged as pattern day trader. 90-day restriction unless
equity is brought above $25,000.
```

### Agent Checklist

A list of boolean checks an agent can run before taking action. These should be implementable as code -- no subjective judgment required.

```markdown
## Agent Checklist

- [ ] Is the account type margin or cash?
- [ ] What is the current account equity?
- [ ] How many day trades have occurred in the last 5 business days?
- [ ] Will this trade constitute a day trade (same-day open and close)?
- [ ] If this would be day trade #4+ and equity < $25,000, block the trade.
```

### Sources

Authoritative references that can be used to verify the content. Include URLs, document titles, and the date accessed. Do not cite blog posts or Stack Overflow -- use primary sources.

```markdown
## Sources

- FINRA Rule 4210: Margin Requirements
  https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210
- SEC: Pattern Day Trader
  https://www.sec.gov/answers/patterndaytrader.htm
- FINRA: Day-Trading Margin Requirements
  https://www.finra.org/investors/learn-to-invest/advanced-investing/day-trading-margin-requirements-know-rules
```

## Quality Bar

Every content document must meet these criteria before merging:

1. **Sources required.** Every factual claim must be traceable to a primary source (regulator website, official documentation, peer-reviewed publication). No unsourced assertions.

2. **Verified date required.** The `last_verified` frontmatter field must be within the last 6 months. If the content has not been re-verified, update the date after checking sources.

3. **Agent Checklist required.** Every document must include a checklist of boolean checks that an agent can programmatically evaluate.

4. **No ambiguity.** Rules must be specific enough to implement in code. "Be careful with X" is not a rule. "If X > threshold, do Y" is a rule.

5. **Real examples.** Examples must use real tickers, real dates, and real numbers. No `ACME Corp` or `$X`.

## Severity Guidelines

Choose severity based on the impact of an agent not having this knowledge:

| Severity | Criteria | Example |
|---|---|---|
| CRITICAL | Financial loss, regulatory violation, or silent data corruption. Must be checked on every relevant operation. | PDT rule, wash sale rule, stock split handling |
| HIGH | Incorrect behavior or degraded performance that requires debugging. Should be checked on first use of a system. | yfinance silent failures, trading hours reference |
| MEDIUM | Increases robustness or reduces debugging time. Good to check periodically. | Polygon.io rate limits, VWAP calculation notes |
| LOW | Optimization opportunities or nice-to-have context. | Performance tuning tips, alternative data sources |
| INFO | Background information that provides useful context but does not directly affect agent behavior. | Historical context, industry terminology |

## Writing for Agents vs. Writing for Humans

Content in agent-context-hub is consumed by LLMs, not (primarily) by humans. This changes how you should write.

### Be explicit

Humans infer from context. Agents do not. State the rule, the exception, and the boundary condition.

Bad: "The PDT rule applies to frequent traders."
Good: "The PDT rule applies when an account makes 4 or more day trades in a rolling 5-business-day window AND the account type is margin AND the account equity is below $25,000."

### Use structured rules

Agents extract structured information more reliably than they parse prose. Use numbered lists, tables, and checklists instead of paragraphs.

Bad: "There are several things to consider when handling stock splits, including adjusting historical prices, updating position sizes, and modifying open orders."
Good:
```
1. Multiply historical pre-split prices by the inverse split ratio.
2. Multiply position share count by the split ratio.
3. Cancel and resubmit all open orders with adjusted prices and quantities.
```

### Avoid ambiguity

Words like "usually", "sometimes", "might", and "generally" are red flags. If a rule has exceptions, list them explicitly.

Bad: "yfinance sometimes returns adjusted close prices."
Good: "yfinance returns adjusted close prices by default. To get unadjusted prices, pass `auto_adjust=False` to the `download()` function. Prior to yfinance 0.2.28, the default was unadjusted."

### Include machine-parseable data

When possible, include data in formats that agents can directly parse: JSON snippets, code blocks with specific function signatures, tables with exact values.

```json
{
  "market_open": "09:30",
  "market_close": "16:00",
  "timezone": "America/New_York",
  "pre_market_open": "04:00",
  "after_hours_close": "20:00"
}
```

### State what NOT to do

Agents are more likely to avoid mistakes when you explicitly state the incorrect approach alongside the correct one.

```
WRONG: Use close price for VWAP calculation.
RIGHT: Use typical price ((high + low + close) / 3) weighted by volume.
```
