# Agent Integration Guide

How to wire agent-context-hub into your AI agent, regardless of framework.

## Direct Python API

The `ContentRegistry` class is the primary integration point. It parses all content, builds a TF-IDF index, and exposes search, get, and list methods.

### Basic usage

```python
from achub.core.registry import ContentRegistry

# Point to the repo root (where domains/ lives)
registry = ContentRegistry("/path/to/agent-context-hub")
registry.build()

# Search for relevant content
results = registry.search("pattern day trader", domain="trading")
for item in results:
    print(f"{item['content_id']} (score: {item['score']:.3f})")
    print(item["body"][:200])

# Get a specific document by ID
doc = registry.get("trading/regulations/pdt-rule/rules")
if doc:
    metadata = doc["metadata"]
    body = doc["body"]
    print(f"Title: {metadata['title']}")
    print(f"Severity: {metadata['severity']}")
    print(body)

# List all content in a domain/category
items = registry.list_all(domain="trading", category="regulations")
for item in items:
    print(f"{item['content_id']}: {item['metadata']['title']}")
```

### Pre-loading context into an agent prompt

```python
from achub.core.registry import ContentRegistry

def build_system_prompt(task_description: str) -> str:
    """Build a system prompt with relevant domain context injected."""
    registry = ContentRegistry("/path/to/agent-context-hub")
    registry.build()

    # Search for docs relevant to the task
    results = registry.search(task_description, domain="trading")

    context_blocks = []
    for item in results[:3]:  # Top 3 most relevant
        meta = item["metadata"]
        context_blocks.append(
            f"--- {meta['title']} (severity: {meta['severity']}) ---\n"
            f"{item['body']}"
        )

    context = "\n\n".join(context_blocks)
    return (
        f"You are a trading agent. Before taking any action, review the following "
        f"domain knowledge:\n\n{context}\n\n"
        f"Task: {task_description}"
    )
```

## CLI Usage from Subprocess

For agents that prefer shell execution or are not written in Python.

```python
import subprocess
import json

def search_context(query: str) -> list[dict]:
    """Search achub via CLI and parse JSON output."""
    result = subprocess.run(
        ["achub", "search", query, "--domain", "trading", "--format", "json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def get_context(content_id: str) -> str:
    """Retrieve a document in LLM-optimized format."""
    result = subprocess.run(
        ["achub", "get", content_id, "--format", "llm"],
        capture_output=True, text=True
    )
    return result.stdout
```

The `--format llm` option produces a token-efficient output format that strips formatting and focuses on content. Use this when injecting context into prompts where token count matters.

## LangChain Tool

Wrap achub as a LangChain tool that your agent can invoke during reasoning.

```python
from langchain.tools import tool
from achub.core.registry import ContentRegistry

# Build the registry once at startup
registry = ContentRegistry("/path/to/agent-context-hub")
registry.build()

@tool
def lookup_domain_context(query: str) -> str:
    """Search domain knowledge for trading rules, regulations, and gotchas.

    Use this tool BEFORE making trading decisions to check for:
    - Regulatory constraints (PDT rule, wash sales)
    - Data vendor quirks (yfinance silent failures, Polygon rate limits)
    - Market structure rules (trading hours, holidays)
    - Calculation pitfalls (VWAP overnight gaps)

    Args:
        query: Natural language description of what you need to know.

    Returns:
        Relevant domain knowledge or "No relevant context found."
    """
    results = registry.search(query, domain="trading")
    if not results:
        return "No relevant context found."

    # Return top result with metadata
    top = results[0]
    meta = top["metadata"]
    return (
        f"[{meta['severity']}] {meta['title']}\n"
        f"Last verified: {meta.get('last_verified', 'unknown')}\n\n"
        f"{top['body']}"
    )

@tool
def get_trading_rule(content_id: str) -> str:
    """Retrieve a specific trading rule or reference document by its ID.

    Example IDs:
    - trading/regulations/pdt-rule/rules
    - trading/regulations/wash-sale/rules
    - trading/market-structure/trading-hours/reference

    Args:
        content_id: The document ID (e.g., 'trading/regulations/pdt-rule/rules').

    Returns:
        The full document content or an error message.
    """
    doc = registry.get(content_id)
    if doc is None:
        return f"Document '{content_id}' not found."
    return doc["body"]
```

### Using with a LangChain agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [lookup_domain_context, get_trading_rule]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)

agent.run("Should I sell AAPL and buy it back in 2 weeks for tax purposes?")
# Agent will call lookup_domain_context("wash sale rule") before answering
```

## CrewAI Tool

```python
from crewai.tools import BaseTool
from achub.core.registry import ContentRegistry

_registry: ContentRegistry | None = None

def _get_registry() -> ContentRegistry:
    global _registry
    if _registry is None:
        _registry = ContentRegistry("/path/to/agent-context-hub")
        _registry.build()  # Call build() once and reuse
    return _registry

class DomainContextTool(BaseTool):
    name: str = "domain_context_lookup"
    description: str = (
        "Search for domain-specific rules, regulations, and gotchas "
        "before making trading decisions. Input is a natural language query."
    )

    def _run(self, query: str) -> str:
        registry = _get_registry()
        results = registry.search(query)
        if not results:
            return "No relevant context found."

        output = []
        for item in results[:3]:
            meta = item["metadata"]
            output.append(
                f"[{meta['severity']}] {meta['title']}\n{item['body'][:500]}"
            )
        return "\n\n---\n\n".join(output)


class ComplianceCheckTool(BaseTool):
    name: str = "compliance_check"
    description: str = (
        "Check a proposed trade against known regulations (PDT rule, wash sale). "
        "Input is a JSON string with portfolio and trade details."
    )

    def _run(self, portfolio_json: str) -> str:
        import subprocess
        result = subprocess.run(
            ["achub", "check", portfolio_json],
            capture_output=True, text=True
        )
        return result.stdout or result.stderr
```

## MCP Server

The MCP integration exposes achub as a Model Context Protocol server, allowing Claude and other MCP-compatible agents to access content natively.

### Setup

```bash
pip install agent-context-hub[mcp]
achub mcp serve
```

### Claude Desktop configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "achub": {
      "command": "achub",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Available tools

| Tool | Description | Parameters |
|---|---|---|
| `achub_search` | Search content by query | `query`, `domain?` |
| `achub_get` | Retrieve content by ID | `content_id`, `format?` (llm/json/markdown) |
| `achub_check` | Run compliance checks | `domain`, `rules`, `portfolio_json` |
| `achub_list` | List available content | `domain?`, `category?` |

### Example invocations

```
# Claude will call these tools automatically when relevant:

achub_search(query="wash sale rule", domain="trading")
# Returns: ranked list of matching content with scores

achub_get(content_id="trading/regulations/wash-sale/rules", format="llm")
# Returns: token-efficient content for the wash sale rule

achub_check(domain="trading", rules="pdt,wash-sale", portfolio_json='{"account_type": "margin", ...}')
# Returns: {violations: [...], passed: [...], has_violations: true/false}

achub_list(domain="trading", category="regulations")
# Returns: list of all regulation content docs
```

## Best Practices

### Pre-load relevant docs

Do not search achub on every agent step. Instead, identify the relevant domain at the start of a task and pre-load the most critical documents into the agent's context window.

```python
# At task start, load all CRITICAL docs for the domain
critical_docs = [
    item for item in registry.list_all(domain="trading")
    if item["metadata"].get("severity") in ("CRITICAL", "critical")
]
```

### Use --format llm for token efficiency

The `llm` output format strips Rich formatting, collapses whitespace, and produces compact output optimized for LLM context windows. Always use this format when injecting content into prompts.

```bash
achub get trading/regulations/pdt-rule/rules --format llm
```

### Cache the registry

Building the registry scans and parses all Markdown files. For long-running agents, build it once and reuse:

```python
# Build once
registry = ContentRegistry("/path/to/agent-context-hub")
registry.build()

# Reuse across multiple queries
result1 = registry.search("day trading limits")
result2 = registry.search("stock split adjustment")
result3 = registry.get("trading/data-vendors/yfinance/gotchas")
```

### Check severity before acting

Always check the `severity` field of returned content. CRITICAL documents contain rules where violations carry financial or legal consequences -- your agent should treat these as hard constraints, not suggestions.

```python
doc = registry.get("trading/regulations/pdt-rule/rules")
if doc and doc["metadata"]["severity"] in ("CRITICAL", "critical"):
    # This is a hard constraint -- do not proceed without compliance
    pass
```
