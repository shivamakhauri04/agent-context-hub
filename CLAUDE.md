# CLAUDE.md — agent-context-hub

## What This Is

Agent-readable knowledge layer for AI agents. Curated Markdown documents with YAML frontmatter that prevent domain-specific hallucinations in trading, healthcare, legal, and other high-stakes domains.

## Directory Map

| Directory | Purpose |
|---|---|
| `domains/` | Content documents organized by domain/category/topic |
| `src/achub/` | CLI + core library |
| `src/achub/core/` | ContentRegistry, TF-IDF index, parser, schema validation |
| `src/achub/commands/` | CLI commands (search, get, list, check, validate, etc.) |
| `src/achub/integrations/` | MCP server, framework integrations |
| `benchmarks/` | Benchmark scenarios and runner |
| `tests/` | pytest test suite |
| `schemas/` | JSON Schemas for content frontmatter and domain-specific data |
| `examples/` | Usage examples (Python API, LangChain, CrewAI) |
| `docs/` | Architecture, content authoring, agent integration guides |

## Key Architecture

- **ContentRegistry** (`src/achub/core/registry.py`) — Central API. Call `build()` once, then `search()`, `get()`, `list_all()`.
- **Content format** — Markdown + YAML frontmatter. Parsed by `core/parser.py` using `python-frontmatter`.
- **Search** — TF-IDF index in `core/index.py`. Pure Python, no numpy/sklearn.
- **Structured checks** — Machine-parseable YAML checks in content docs, evaluated by `core/checker.py`.
- **CLI entry** — `src/achub/cli.py`. Commands in `src/achub/commands/`.
- **MCP server** — `src/achub/integrations/mcp.py`. Exposes search, get, check, list as MCP tools.

## Dev Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
```

## Testing

```bash
pytest tests/                    # Run all tests
ruff check src/                  # Lint
achub validate --all             # Validate all content docs against schema
```

## Adding Content

1. Create `.md` file in `domains/{domain}/{category}/{topic}/`
2. Add YAML frontmatter matching `schemas/content-frontmatter.json`
3. Include: Summary, The Problem, Rules, Examples, Agent Checklist, Structured Checks, Sources
4. Run `achub validate --all` to verify

## Conventions

- Python 3.10+, 4-space indent, line-length 100
- Conventional commits (`fix:`, `feat:`, `docs:`, `refactor:`)
- Ruff for linting: `select = ["E", "F", "I", "N", "W", "UP"]`
- Never commit `.env`, `.venv`, `__pycache__`, credentials
