# agent-context-hub

**Stop your AI agent from hallucinating domain knowledge.**

The missing knowledge layer for AI agents. Curated, agent-readable context documents that prevent costly mistakes in trading, healthcare, legal, and more.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)

---

## Why This Exists

AI agents hallucinate domain-specific rules. An LLM asked to build a trading bot will confidently generate code that violates SEC regulations, miscalculates VWAP across overnight gaps, or ignores wash sale windows -- mistakes that carry real financial and legal consequences. The agent does not know what it does not know, and there is no error message when it invents a rule that does not exist or ignores one that does.

The context-file pattern -- pioneered by projects like CLAUDE.md, AGENTS.md, and [andrewyng/aisuite](https://github.com/andrewyng/aisuite) -- proved that giving an AI structured, domain-specific documents dramatically improves accuracy for coding tasks. **agent-context-hub extends this pattern to every high-stakes domain**: trading, healthcare, legal, education, and beyond.

Instead of hoping your agent "knows" the PDT rule, you give it a verified, structured document it can reference before making decisions. Every document includes severity levels, agent checklists, real-world examples, and primary-source citations. The result: fewer hallucinations, fewer costly mistakes, and agents that know the boundaries of their knowledge.

## Quick Start

### Install

```bash
pip install agent-context-hub
```

Or install from source:

```bash
git clone https://github.com/shivamakhauri/agent-context-hub.git
cd agent-context-hub
pip install -e .
```

### Three commands to get started

```bash
# List all available content documents
achub list --domain trading

# Search for relevant context using natural language
achub search "wash sale tax implications" --domain trading

# Retrieve a specific document in agent-optimized format
achub get trading/regulations/wash-sale/rules --format llm
```

### Output formats

| Format | Flag | Use case |
|---|---|---|
| `markdown` | `--format markdown` | Human-readable Rich terminal output (default) |
| `json` | `--format json` | Structured output for programmatic consumption |
| `llm` | `--format llm` | Token-efficient format optimized for LLM context windows |

## What's Inside (Trading Launch)

The trading domain ships with 8 curated content documents across 6 categories. Each document has been verified against primary sources and structured for agent consumption.

| Content ID | Title | Severity | Description |
|---|---|---|---|
| `trading/regulations/pdt-rule/rules` | Pattern Day Trader (PDT) Rule | CRITICAL | FINRA Rule 4210 restricting day trades in margin accounts under $25k equity. Violation triggers 90-day freeze. |
| `trading/regulations/wash-sale/rules` | IRS Wash Sale Rule | CRITICAL | 30-day window rule that disallows tax-loss harvesting on substantially identical securities. |
| `trading/market-structure/trading-hours/reference` | US Equity Market Trading Hours | HIGH | NYSE/NASDAQ regular, pre-market, and after-hours sessions. Holiday schedule. |
| `trading/broker-apis/alpaca/quirks` | Alpaca Broker API Quirks | HIGH | Paper vs live environment differences, order lifecycle edge cases, WebSocket gotchas. |
| `trading/corporate-actions/stock-splits/handling` | Stock Split Detection and Handling | CRITICAL | How to detect splits, adjust historical prices, and avoid interpreting a 75% split as a crash. |
| `trading/data-vendors/polygon/gotchas` | Polygon.io Integration Pitfalls | MEDIUM | Rate limits, data gaps, schema changes between API versions, timestamp timezone handling. |
| `trading/data-vendors/yfinance/gotchas` | yfinance Silent Failures | HIGH | Adjusted vs unadjusted close confusion, silent NaN returns on delisted tickers, timezone issues. |
| `trading/technical-indicators/vwap/gotchas` | VWAP Calculation Gotchas | MEDIUM | Overnight gap handling, intraday reset boundaries, volume weighting formula. |

### Severity levels

| Severity | Meaning |
|---|---|
| CRITICAL | Financial loss, regulatory violation, or silent data corruption. Must be checked every time. |
| HIGH | Incorrect behavior requiring debugging. Check on first use and periodically. |
| MEDIUM | Improves robustness and reduces debugging time. |
| LOW | Optimization opportunities and nice-to-have context. |

## Benchmark Suite

The benchmark suite tests whether an AI agent correctly handles real-world edge cases. These are not toy examples -- they are drawn from actual market scenarios that have caused losses for both human traders and automated systems.

| # | Scenario | What It Tests | Difficulty |
|---|---|---|---|
| 1 | AAPL 4:1 Stock Split (Aug 2020) | Agent recognizes a 75% price drop as a split, not a crash | Medium |
| 2 | Pattern Day Trader Violation | Agent blocks the 4th day trade on a $15k margin account | Hard |
| 3 | Wash Sale 30-Day Window | Agent detects repurchase of TSLA within 30 days of a tax-loss sale | Hard |
| 4 | VWAP Overnight Gap | Agent rejects VWAP that includes overnight data in its calculation | Medium |
| 5 | yfinance Adjusted Close | Agent uses `auto_adjust=False` when backtesting pre-split data | Easy |

### Running benchmarks

```bash
# Run all trading benchmarks
achub benchmark run --domain trading

# Output includes pass/fail for each scenario plus a summary score
```

### Benchmark badge

Add a benchmark badge to your project README to show compliance:

```markdown
![Trading Benchmark](https://img.shields.io/badge/achub--trading--benchmark-5%2F5%20passed-brightgreen)
```

Color thresholds:
- 100% pass: `brightgreen`
- 60-99% pass: `yellow`
- Below 60%: `red`

### Adding custom scenarios

You can add your own benchmark scenarios by creating YAML files in `benchmarks/domains/<domain>/scenarios/` and registering them in the domain's `suite.yaml`. See [benchmarks/README.md](benchmarks/README.md) for the full format.

## Agent Integration

### Python API (5 lines)

```python
from achub.core.registry import ContentRegistry

registry = ContentRegistry("/path/to/agent-context-hub")
registry.build()
results = registry.search("pattern day trader")
context = registry.get("trading/regulations/pdt-rule/rules")
```

The `ContentRegistry` scans all domains, parses all Markdown files, and builds a TF-IDF index. Call `build()` once, then use `search()`, `get()`, and `list_all()` as needed.

### LangChain Tool

```python
from langchain.tools import tool
from achub.core.registry import ContentRegistry

registry = ContentRegistry("/path/to/agent-context-hub")
registry.build()

@tool
def lookup_trading_context(query: str) -> str:
    """Search agent-context-hub for trading rules, regulations, and gotchas.

    Use this BEFORE making trading decisions to check for regulatory
    constraints, data vendor quirks, and calculation pitfalls.
    """
    results = registry.search(query, domain="trading")
    if not results:
        return "No relevant context found."
    top = results[0]
    meta = top["metadata"]
    return (
        f"[{meta['severity']}] {meta['title']}\n\n"
        f"{top['body']}"
    )
```

### CrewAI Tool

```python
from crewai.tools import BaseTool
from achub.core.registry import ContentRegistry

class DomainContextTool(BaseTool):
    name: str = "domain_context_lookup"
    description: str = "Look up domain-specific rules and gotchas before making trading decisions."

    def _run(self, query: str) -> str:
        registry = ContentRegistry("/path/to/agent-context-hub")
        registry.build()
        results = registry.search(query)
        if not results:
            return "No relevant context found."
        return results[0]["body"]
```

### MCP Server (coming soon)

The MCP integration will expose achub content as Model Context Protocol resources and tools, enabling Claude and other MCP-compatible agents to access domain knowledge natively.

```bash
pip install agent-context-hub[mcp]
achub mcp serve
```

See [docs/agent-integration.md](docs/agent-integration.md) for complete integration patterns, best practices, and advanced usage.

## CLI Reference

| Command | Description | Key Options |
|---|---|---|
| `achub list` | List all content documents | `--domain`, `--category` |
| `achub search <query>` | Full-text TF-IDF search | `--domain`, `--limit` |
| `achub get <content_id>` | Retrieve a document by ID | `--format markdown\|json\|llm` |
| `achub validate [path]` | Validate frontmatter against schema | `--all` for all files |
| `achub check <portfolio>` | Run compliance checks (PDT, wash sale) | Portfolio as JSON input |
| `achub regime` | Current market regime and session info | Trading day status, hours |
| `achub annotate <content_id>` | Add notes to a content document | Stored in `.achub/annotations/` |
| `achub feedback <content_id>` | Rate and comment on content | Stored in `.achub/feedback/` |
| `achub benchmark run` | Run benchmark scenarios | `--domain` |

### Examples

```bash
# List only regulation content
achub list --domain trading --category regulations

# Search with a result limit
achub search "stock split detection" --domain trading --limit 3

# Get content as JSON for programmatic use
achub get trading/corporate-actions/stock-splits/handling --format json

# Validate all content across all domains
achub validate --all

# Check current market status
achub regime
```

## Architecture

```
domains/                         Content Layer
  trading/                       (Markdown + YAML frontmatter)
    DOMAIN.md
    regulations/
      pdt-rule/rules.md
      wash-sale/rules.md
    market-structure/
    broker-apis/
    corporate-actions/
    data-vendors/
    technical-indicators/
       |
       v
src/achub/core/                  Core Layer
  parser.py                      Parse markdown, extract frontmatter
  index.py                       TF-IDF search index (pure Python, no numpy)
  registry.py                    Central content registry and query API
  schema.py                      JSON Schema validation
  domain.py                      Domain discovery
       |
       v
src/achub/commands/              CLI Layer
  list.py                        List content with filters
  search.py                      Full-text search
  get.py                         Retrieve by ID
  validate.py                    Schema validation
  check.py                       Compliance rule checks
  regime.py                      Market regime info
  annotate.py                    Content annotations
  feedback.py                    Content feedback
  benchmark.py                   Benchmark runner
       |
       v
src/achub/integrations/          Integration Layer
  mcp.py                         MCP server (planned)
                                 LangChain / CrewAI via Python API
       |
       v
  Your Agent                     Consumer
```

Key design decisions:
- **Markdown + frontmatter**: Human-writable, git-friendly, agent-readable. No database needed.
- **TF-IDF search**: Zero external dependencies, deterministic, fast at this scale. No API keys or embedding models.
- **File-based storage**: Clone the repo and you have everything. No Docker, no server process.

See [docs/architecture.md](docs/architecture.md) for the full design rationale and data flow.

## Adding a New Domain

Adding a new domain is a four-step process:

1. **Create the domain directory**: `mkdir -p domains/your-domain`
2. **Write DOMAIN.md** with required frontmatter: `id`, `title`, `version`, `description`, `categories`, `maintainers`
3. **Add content documents** following the [standard format](docs/content-authoring.md) -- each with YAML frontmatter, Summary, The Problem, Rules, Examples, Agent Checklist, and Sources sections
4. **Submit a PR** -- CI will run `achub validate --all` to check schema compliance

The quality bar: every document must have primary-source citations, a verified date within 6 months, and an agent-actionable checklist. No unsourced claims.

See [docs/adding-a-domain.md](docs/adding-a-domain.md) for the full step-by-step guide including schemas, benchmarks, and the PR checklist.

## Roadmap

| Domain | Target | Status | Planned Content |
|---|---|---|---|
| Trading | Now | Shipped (v0.1.0) | 8 docs across regulations, market structure, broker APIs, corporate actions, data vendors, technical indicators |
| Healthcare | Q2 2026 | In planning | Drug interactions, dosage calculations, contraindication rules, FDA compliance |
| Legal | Q3 2026 | In planning | Contract review patterns, regulatory compliance checks, jurisdiction-specific rules |
| Education | Q4 2026 | In planning | Curriculum standards, assessment validity rules, accessibility requirements (WCAG, Section 508) |

We are actively seeking domain experts to contribute. If you have deep knowledge in healthcare, legal, or education and want to help build the knowledge layer for AI agents in your field, open an issue or reach out.

## Contributing

We welcome contributions of all kinds:

- **New domains** -- Bring your domain expertise (see [docs/adding-a-domain.md](docs/adding-a-domain.md))
- **New content documents** -- Add coverage to existing domains
- **Benchmark scenarios** -- Write edge-case tests for agents
- **Core improvements** -- Better search, new output formats, framework integrations

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on content quality standards, frontmatter schema requirements, writing for agents (not humans), and the PR review process.

## License

MIT. See [LICENSE](LICENSE) for details.

---

Built by [Shivam Akhauri](https://github.com/shivamakhauri). Inspired by the context-file pattern pioneered in AI-assisted coding.
