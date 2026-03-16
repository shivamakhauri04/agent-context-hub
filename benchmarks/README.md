# Can Your Agent Pass?

Benchmarks test whether an AI trading agent correctly handles real-world edge cases. These are not toy examples -- they are drawn from actual market scenarios that have tripped up both human traders and automated systems.

## Scenarios

| # | Name | Tests | Difficulty |
|---|------|-------|------------|
| 1 | AAPL 4:1 Stock Split (2020) | Recognizes a stock split vs. a crash | Medium |
| 2 | Pattern Day Trader Violation | Blocks trades that would trigger PDT restriction | Hard |
| 3 | Wash Sale 30-Day Window | Detects wash sale violations within 30-day window | Hard |
| 4 | VWAP Overnight Gap | Rejects VWAP computed across overnight gaps | Medium |
| 5 | yfinance Adjusted Close | Distinguishes adjusted vs. unadjusted close prices | Easy |

## Running Benchmarks

```bash
achub benchmark run --domain trading
```

This loads the suite definition from `benchmarks/domains/trading/suite.yaml`, runs each scenario, and prints a pass/fail report.

## Badge

Add a benchmark badge to your README:

```markdown
![Trading Benchmark](https://img.shields.io/badge/achub--trading--benchmark-5%2F5%20passed-brightgreen)
```

Replace `5%2F5%20passed` with your actual score (e.g., `3%2F5%20passed` becomes a yellow badge, `1%2F5%20passed` becomes red).

Color thresholds:
- 100%: `brightgreen`
- 60-99%: `yellow`
- <60%: `red`

## Adding Custom Scenarios

1. Create a new YAML file in `benchmarks/domains/<domain>/scenarios/`:

```yaml
id: my_custom_scenario
description: "Description of the edge case being tested."
input:
  # Inputs your agent will receive
  key: value
expected:
  # Expected outputs to validate against
  key: value
context_docs:
  - "domain/category/topic/doc-id"
```

2. Register it in `benchmarks/domains/<domain>/suite.yaml`:

```yaml
scenarios:
  - name: "My Custom Scenario"
    file: "my_custom_scenario.yaml"
    difficulty: "medium"
    tags: ["custom"]
```

3. Run the suite again to include your new scenario.
