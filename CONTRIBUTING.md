# Contributing to agent-context-hub

Thank you for your interest in contributing. This project grows through community contributions of real-world domain knowledge that helps AI agents avoid costly mistakes.

## Getting Started

1. **Fork and clone** the repository:

   ```bash
   git clone https://github.com/<your-username>/agent-context-hub.git
   cd agent-context-hub
   ```

2. **Install in development mode:**

   ```bash
   pip install -e ".[dev]"
   ```

   This installs the `achub` CLI, all runtime dependencies, and dev tools (ruff, pytest).

## Types of Contributions

### New content documents (easiest way to contribute)

Content documents are Markdown files containing domain-specific knowledge that AI agents need but typically lack. If you have seen an agent make a mistake because it did not know a domain rule, regulation, or gotcha, that is a content contribution.

### New domains

If the domain you want to contribute to does not exist yet, you can propose a new top-level domain directory under `content/`. Open a "New Content Request" issue first to discuss the scope.

### CLI features

Improvements to the `achub` CLI tool -- new commands, better validation, output formats, etc.

### Benchmarks

Test cases that evaluate whether an agent correctly applies the knowledge from a content document.

## Adding a Content Document

1. **Identify the correct path.** Content documents live under `content/<domain>/<category>/`. For example: `content/trading/regulations/pdt-rule.md`.

2. **Use the frontmatter template.** Every content document must begin with YAML frontmatter containing all required fields. See `CONTENT_STANDARDS.md` for the full specification.

3. **Follow the quality bar.** Read `CONTENT_STANDARDS.md` before writing. Key requirements:
   - All required frontmatter fields must be present and valid
   - Must include a Sources section with verifiable links
   - Must include an Agent Checklist section (machine-actionable)
   - `last_verified` must be within 6 months
   - No marketing language -- factual, precise, actionable
   - Examples must use real tickers, real dates, real numbers
   - Must be verified against primary sources

4. **Validate your document:**

   ```bash
   achub validate content/trading/regulations/pdt-rule.md
   ```

## Running Checks

Before submitting a PR, make sure all checks pass:

```bash
# Validate all content documents
achub validate --all

# Run tests
pytest -v

# Lint and format check
ruff check src/
ruff format --check src/
```

## PR Process

1. **Create a branch** from `main`:

   ```bash
   git checkout -b content/trading/pdt-rule
   ```

2. **Make your changes** following the standards above.

3. **Run all checks** (validate, test, lint).

4. **Push and open a PR.** Fill out the PR template completely. Link any related issues.

5. **Respond to review feedback.** PRs require at least one approving review before merge.

## Commit Messages

Use conventional commits:

- `feat: add PDT rule content document`
- `fix: correct wash sale holding period`
- `docs: update contributing guide`
- `refactor: simplify validator logic`

## Code of Conduct

Be respectful, constructive, and factual. This project deals with domain knowledge that has real financial, legal, and safety implications. Accuracy matters more than speed. If you are unsure about a claim, cite your source or flag it for review.
