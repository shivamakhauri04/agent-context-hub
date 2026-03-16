# Adding a New Domain

Step-by-step guide for contributing a new domain to agent-context-hub.

## Overview

A domain is a top-level knowledge area (e.g., trading, healthcare, legal). Each domain contains categorized content documents that capture rules, gotchas, and reference data that AI agents need to avoid costly mistakes.

## Step 1: Create the Domain Directory

```bash
mkdir -p domains/your-domain
```

Choose a lowercase, hyphenated name that clearly identifies the knowledge area:
- `healthcare` (not `health-care` or `medical`)
- `real-estate` (not `realestate`)
- `tax-law` (not `taxes`)

## Step 2: Write DOMAIN.md

Every domain must have a `DOMAIN.md` file at its root. This is the domain manifest -- it defines the domain's identity, categories, and usage guidance.

```markdown
---
id: "your-domain"
title: "Your Domain Name"
version: "1.0.0"
description: "One-sentence description of what this domain covers."
categories:
  - category-one
  - category-two
  - category-three
maintainers: ["your-github-username"]
---

# Your Domain Name

## Purpose

One paragraph explaining why this domain exists and what problems it prevents
for AI agents.

## Taxonomy of Categories

### category-one
Description of what this category covers and why agents need it.

### category-two
Description of what this category covers and why agents need it.

## How Agents Should Use This Content

Numbered list of guidance for when and how agents should consult these docs.

## Severity Levels

| Severity | Meaning |
|----------|---------|
| CRITICAL | Can cause harm, violations, or data corruption. Must be checked every time. |
| HIGH | Can cause incorrect behavior. Should be checked on first use. |
| MEDIUM | Good to know. Reduces debugging time. |
| LOW | Nice-to-have context. |

## Document Format

Describe the standard sections used in content documents for this domain.
```

### Required frontmatter fields for DOMAIN.md

| Field | Type | Description |
|---|---|---|
| `id` | string | Domain identifier, must match directory name |
| `title` | string | Human-readable domain name |
| `version` | string | Semantic version (e.g., `1.0.0`) |
| `description` | string | One-sentence description |
| `categories` | list | Valid category names for this domain |
| `maintainers` | list | GitHub usernames of domain maintainers |

## Step 3: Add Content Documents

Create category directories and content documents following the standard format. See [content-authoring.md](content-authoring.md) for detailed writing guidance.

### Directory structure

```
domains/your-domain/
  DOMAIN.md
  category-one/
    topic-name/
      rules.md          # or gotchas.md, reference.md, handling.md
  category-two/
    another-topic/
      rules.md
```

### Content document naming conventions

- Use lowercase, hyphenated directory names for topics: `pdt-rule`, `stock-splits`, `trading-hours`
- Use descriptive filenames that indicate the document type:
  - `rules.md` -- Regulatory or compliance rules
  - `gotchas.md` -- Pitfalls, quirks, and failure modes
  - `reference.md` -- Reference data and lookup tables
  - `handling.md` -- How to handle specific situations
  - `quirks.md` -- API or system-specific quirks

### Required frontmatter for content documents

Every content document must have YAML frontmatter that passes schema validation:

```yaml
---
id: "your-domain/category/topic/doc-type"
title: "Human-Readable Title"
domain: "your-domain"
version: "1.0.0"
category: "category-name"
tags:
  - relevant-tag-1
  - relevant-tag-2
severity: "CRITICAL"    # CRITICAL | HIGH | MEDIUM | LOW | INFO
last_verified: "2026-03-01"
applies_to:
  - trading-agents
  - portfolio-systems
related:
  - "your-domain/category/other-topic/doc"
---
```

## Step 4: Add Schemas (Optional)

If your domain has specific validation requirements beyond the base schema, add a domain-specific schema:

```bash
mkdir -p schemas/domains/your-domain
```

Create a JSON Schema file that extends the base `schemas/content-frontmatter.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "allOf": [
    { "$ref": "../../content-frontmatter.json" },
    {
      "properties": {
        "domain": { "const": "your-domain" },
        "category": { "enum": ["category-one", "category-two"] }
      }
    }
  ]
}
```

## Step 5: Add Benchmark Scenarios

Create benchmark scenarios that test whether an agent correctly applies the domain knowledge:

```bash
mkdir -p benchmarks/domains/your-domain/scenarios
```

### Create a suite definition

```yaml
# benchmarks/domains/your-domain/suite.yaml
domain: your-domain
version: "1.0.0"
scenarios:
  - name: "Descriptive Scenario Name"
    file: "scenario_one.yaml"
    difficulty: "medium"
    tags: ["category-one"]
```

### Create scenario files

```yaml
# benchmarks/domains/your-domain/scenarios/scenario_one.yaml
id: scenario_one
description: "A real-world edge case that tests the agent's domain knowledge."
input:
  # What the agent receives
  question: "Should I do X given Y conditions?"
  data:
    key: value
expected:
  # What the agent should conclude
  action: "do_not_proceed"
  reason: "Violates rule Z"
context_docs:
  - "your-domain/category/topic/rules"
```

## Step 6: Validate

Run validation to ensure all frontmatter conforms to the schema:

```bash
# Validate a single file
achub validate domains/your-domain/category-one/topic-name/rules.md

# Validate everything
achub validate --all
```

Fix any validation errors before submitting.

## Step 7: Submit a PR

1. Create a branch: `git checkout -b domain/your-domain`
2. Commit your changes with a descriptive message: `feat: add your-domain domain with N content documents`
3. Push and open a PR against `main`
4. In the PR description, include:
   - What the domain covers
   - How many content documents are included
   - What severity levels are represented
   - Which benchmark scenarios are included

### PR checklist

- [ ] `DOMAIN.md` exists with all required frontmatter fields
- [ ] All content documents have valid frontmatter (`achub validate --all` passes)
- [ ] Every content document has Sources section with verifiable references
- [ ] Every content document has an Agent Checklist section
- [ ] `last_verified` dates are within the last 6 months
- [ ] At least one benchmark scenario is included
- [ ] Domain is listed in categories of `DOMAIN.md`
