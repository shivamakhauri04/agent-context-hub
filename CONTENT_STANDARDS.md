# Content Standards

This document defines the quality bar for content documents in agent-context-hub. Every content document must meet these standards before it can be merged.

## Required Frontmatter Fields

Every content document must begin with YAML frontmatter containing all of the following fields:

| Field | Type | Description |
|---|---|---|
| `title` | string | Clear, descriptive title of the rule or gotcha |
| `domain` | string | Top-level domain (e.g., `trading`, `healthcare`, `legal`) |
| `category` | string | Subcategory within the domain (e.g., `regulations`, `data-vendors`) |
| `severity` | string | One of: `critical`, `high`, `medium`, `low` |
| `last_verified` | date | Date when the content was last verified against primary sources (YYYY-MM-DD) |
| `tags` | list | Relevant tags for discovery and filtering |

All fields must be present and non-empty. The validator (`achub validate`) checks this automatically.

## Severity Levels

Severity must be justified by the potential impact of an agent not knowing this information:

- **critical** -- Can cause direct financial loss, legal liability, or safety risk. Example: violating the Pattern Day Trader rule triggers an account freeze.
- **high** -- Can cause significant operational failures or incorrect outputs that are hard to detect. Example: using unadjusted price data for backtesting produces misleading results.
- **medium** -- Can cause suboptimal decisions or minor errors. Example: not accounting for settlement delays when calculating available capital.
- **low** -- Nice-to-know context that improves quality but is unlikely to cause harm if missing.

## Required Sections

### Sources

Every content document must include a `## Sources` section containing links to primary, verifiable sources. Acceptable sources include:

- Official regulatory documents (SEC, FINRA, FDA, etc.)
- Exchange or broker documentation
- Peer-reviewed publications
- Official government or institutional websites

Blog posts, LLM-generated summaries, and social media are not acceptable as primary sources. They may be included as supplementary context but must not be the sole reference.

### Agent Checklist

Every content document must include a `## Agent Checklist` section with machine-actionable items. These are concrete checks that an AI agent can evaluate programmatically or as part of its reasoning. Format each item as a Markdown checklist entry:

```markdown
## Agent Checklist
- [ ] Verify account equity exceeds $25,000 before executing 4th day trade in 5 business days
- [ ] Check if security is hard-to-borrow before attempting short sale
- [ ] Confirm market hours for the specific exchange before placing time-sensitive orders
```

## Verification Requirements

- The `last_verified` date must be within 6 months of the current date. Content older than 6 months must be re-verified before merge.
- Verification means checking the claims in the document against the cited primary sources and confirming they are still accurate.
- If a regulation or rule has changed, the document must be updated to reflect the current state.

## Writing Style

- **No marketing language.** Do not use phrases like "game-changing," "revolutionary," "best-in-class," or similar. State facts.
- **Factual, precise, actionable.** Every sentence should convey specific, useful information. Avoid vague statements like "be careful with X."
- **Use real examples.** When illustrating a rule, use real tickers, real dates, and real numbers. Do not use placeholders like "Stock ABC" or "some amount." If you need a hypothetical, ground it in realistic values.
- **Cite specific thresholds and numbers.** Instead of "accounts with low equity," write "accounts with equity below $25,000."
- **Write for machines as much as humans.** Content will be consumed by AI agents. Be explicit and unambiguous.

## Primary Source Requirement

Content must be verified against primary sources. Do not rely solely on LLM-generated knowledge, which may be outdated or incorrect. The purpose of this project is to provide agents with verified, current domain knowledge that goes beyond what is in their training data.

If you cannot find a primary source for a claim, either:
1. Remove the claim, or
2. Mark it explicitly as unverified and open an issue to track verification.
