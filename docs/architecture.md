# Architecture

This document describes how agent-context-hub is structured, how data flows through the system, and why key design decisions were made.

## System Layers

### 1. Content Layer (`domains/`)

The content layer is a directory tree of Markdown files with YAML frontmatter. Each domain gets its own top-level directory under `domains/`, with a `DOMAIN.md` manifest and categorized content documents underneath.

```
domains/
  trading/
    DOMAIN.md                              # Domain manifest
    regulations/
      pdt-rule/rules.md                    # Content document
      wash-sale/rules.md
    market-structure/
      trading-hours/reference.md
    broker-apis/
      alpaca/quirks.md
    corporate-actions/
      stock-splits/handling.md
    data-vendors/
      polygon/gotchas.md
      yfinance/gotchas.md
    technical-indicators/
      vwap/gotchas.md
```

**DOMAIN.md** contains domain-level metadata:
- `id`: Domain identifier (e.g., `trading`)
- `title`: Human-readable name
- `version`: Semantic version
- `description`: What the domain covers
- `categories`: List of valid categories within the domain
- `maintainers`: GitHub usernames of domain maintainers

**Content documents** contain:
- YAML frontmatter with required fields: `id`, `title`, `domain`, `version`, `category`, `tags`, `severity`, `last_verified`
- Optional fields: `applies_to`, `related`
- Markdown body with standard sections: Summary, The Problem, Rules, Examples, Agent Checklist, Sources

### 2. Core Layer (`src/achub/core/`)

The core layer provides parsing, indexing, validation, and registry services.

**parser.py** -- Reads Markdown files and extracts YAML frontmatter using the `python-frontmatter` library. Returns a dict with `metadata`, `body`, and `path` keys. Handles malformed files gracefully with warnings.

**index.py** -- A pure-Python TF-IDF search index built on the `math` module (no numpy/scipy dependency). Tokenizes text by splitting on whitespace and punctuation, computes term frequency normalized by document length, and scores queries using TF-IDF with `log(N/df)` weighting.

**registry.py** -- The central `ContentRegistry` class that ties everything together:
1. Discovers all domains under `domains/`
2. Parses all `.md` files in each domain
3. Assigns content IDs based on file paths (e.g., `trading/regulations/pdt-rule/rules`)
4. Builds the TF-IDF index over all content
5. Exposes `get()`, `list_all()`, and `search()` methods

**schema.py** -- Validates frontmatter metadata against a JSON Schema (`schemas/content-frontmatter.json`). Uses `jsonschema.Draft7Validator` and returns a list of human-readable error messages.

**domain.py** -- Domain discovery utilities. Scans `domains/` for subdirectories containing a `DOMAIN.md` file and resolves domain paths.

### 3. CLI Layer (`src/achub/commands/`)

The CLI is built with Click and uses Rich for terminal output. Each command is a separate module:

| Module | Command | Purpose |
|---|---|---|
| `list.py` | `achub list` | List content with optional `--domain` and `--category` filters |
| `search.py` | `achub search` | TF-IDF search with `--domain` filter and `--limit` |
| `get.py` | `achub get` | Retrieve content by ID in markdown, json, or llm format |
| `validate.py` | `achub validate` | Validate frontmatter against JSON Schema |
| `check.py` | `achub check` | Run compliance rule checks against portfolio data |
| `regime.py` | `achub regime` | Market regime and trading day info |
| `annotate.py` | `achub annotate` | Add notes to content items (stored in `.achub/annotations/`) |
| `feedback.py` | `achub feedback` | Rate and comment on content quality (stored in `.achub/feedback/`) |
| `benchmark.py` | `achub benchmark` | Run benchmark scenarios from YAML suite definitions |

All commands receive the project root via Click's context object, instantiate a `ContentRegistry`, and call `registry.build()` before performing their operation.

### 4. Integration Layer (`src/achub/integrations/`)

**MCP server** (`mcp.py`) -- Planned integration to expose achub content as MCP resources and tools for Claude and other MCP-compatible agents. Will provide:
- `achub://content/{content_id}` resources
- `achub_search` tool
- `achub_check` tool

**Python API** -- The `ContentRegistry` class is the primary integration point. Any Python agent framework (LangChain, CrewAI, AutoGen) can instantiate a registry, build the index, and call `search()` or `get()` directly.

**CLI subprocess** -- Agents that prefer shell execution can call `achub` commands and parse the output (use `--format json` or `--format llm` for structured output).

### 5. Schema Layer (`schemas/`)

JSON Schema files that define the required structure of content frontmatter:

- `schemas/content-frontmatter.json` -- Base schema for all content documents
- `schemas/domains/<domain>/` -- Domain-specific schema extensions (planned)

## Data Flow

```
1. DISCOVERY
   domains/ -> domain.py discovers dirs with DOMAIN.md
                |
2. PARSING      v
   *.md files -> parser.py extracts frontmatter + body
                |
3. INDEXING     v
   parsed docs -> registry.py assigns content IDs
              -> index.py builds TF-IDF index
                |
4. QUERY        v
   user/agent -> CLI command or Python API
              -> registry.search() / registry.get() / registry.list_all()
                |
5. OUTPUT       v
   results -> formatting.py renders as markdown/json/llm
           -> returned to user or agent
```

## Design Decisions

### Why Markdown with YAML frontmatter?

- **Human-readable and human-editable.** Contributors can write content in any text editor. No special tooling required.
- **Git-friendly.** Diffs are meaningful. PRs show exactly what changed in the domain knowledge.
- **Agent-readable.** Markdown is the most common format LLMs are trained on. YAML frontmatter provides structured metadata for programmatic filtering without a database.
- **Proven pattern.** CLAUDE.md, AGENTS.md, and similar context files have demonstrated that this format works well for AI agents.

### Why TF-IDF instead of vector embeddings?

- **Zero external dependencies.** No API keys, no embedding models, no vector databases. The index is built using only Python's `math` module.
- **Deterministic.** Same query always returns the same results. No model version drift.
- **Fast enough.** With dozens to hundreds of documents, TF-IDF provides sub-millisecond search. Vector search adds complexity without meaningful quality improvement at this scale.
- **Offline.** Works without network access. Important for air-gapped or CI/CD environments.

### Why no database?

- **The filesystem is the database.** Content lives in `domains/` as files. The registry rebuilds its in-memory index on every invocation. This is fast enough for the expected document count (hundreds, not millions).
- **Simplicity.** No migrations, no connection strings, no state management. Clone the repo and you have everything.
- **Portability.** Works anywhere Python runs. No Docker, no server process.

### Why Click for the CLI?

- **Mature and well-documented.** Click handles argument parsing, help text, and shell completion.
- **Composable.** Each command is a separate module. Adding a new command is one file plus one line in `cli.py`.
- **Rich integration.** Click works cleanly with Rich for formatted terminal output.

### Why JSON Schema for validation?

- **Standard.** JSON Schema is widely supported and well-understood.
- **Declarative.** The schema file (`schemas/content-frontmatter.json`) is the single source of truth for what frontmatter fields are required.
- **Extensible.** Domain-specific schemas can extend the base schema without code changes.
