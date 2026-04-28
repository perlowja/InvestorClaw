# InvestorClaw Command Reference

Version `2.1.9` documents the complete command surface.

## Important Disclaimer

InvestorClaw is an educational portfolio analysis tool.

It is not a fiduciary advisor.

It does not provide investment advice.

It helps you have informed conversations with your financial advisor.

Always consult a qualified financial professional before making investment decisions.

## Command Categories

### Portfolio Analysis

Use these commands to analyze portfolio holdings, returns, and fixed income exposure.

| Command | Aliases | Natural Language | Output | Purpose |
|---------|---------|------------------|--------|---------|
| `holdings` | `snapshot`, `prices` | "What's in my portfolio?", "Show my holdings" | `holdings.json` | Live price snapshot, concentration ratios, sector weights |
| `performance` | `analyze`, `returns` | "How am I doing?", "Am I beating the market?" | `performance.json` | Sharpe ratio, beta, max drawdown, volatility |
| `bonds` | `bond-analysis`, `analyze-bonds`, `bond-exposure`, `bond-allocation` | "Show my bond exposure", "Analyze my fixed income" | `bond_analysis.json` | YTM, duration, modified duration, convexity, FRED benchmarks |
| `fixed-income` | `fixed-income-analysis`, `bond-strategy` | "Fixed income strategy", "Bond analysis" | `fixed_income_analysis.json` | Fixed income strategy analysis, sector breakdown |
| `analysis` | `portfolio-analysis` | "Analyze my portfolio", "Portfolio overview" | `portfolio_analysis.json` | Comprehensive multi-factor analysis |
| `synthesize` | `multi-factor`, `recommend` | "Synthesize my portfolio", "Give me a summary" | `portfolio_analysis.json` | LLM synthesis + key insights (requires consultation model) |

### Market Data

Use these commands to inspect analyst views, news, and ticker details.

| Command | Aliases | Natural Language | Output | Purpose |
|---------|---------|------------------|--------|---------|
| `analyst` | `analysts`, `ratings` | "What does Wall Street think?", "Analyst ratings" | `analyst_data.json` | Analyst consensus ratings, price targets |
| `news` | `sentiment` | "Any news on my stocks?", "Portfolio news" | `portfolio_news.json` | Portfolio news correlation, sentiment analysis |
| `lookup` | `query`, `detail` | "Tell me about AAPL", "What's NVDA worth?" | stdout | Quick price, analyst data, or news for any ticker |

### Portfolio Optimization

Use this command to rebalance a portfolio or generate an efficient frontier.

| Command | Aliases | Natural Language | Output | Purpose |
|---------|---------|------------------|--------|---------|
| `optimize` | `rebalance`, `allocation`, `efficient-frontier` | "How should I rebalance?", "Maximize Sharpe ratio" | `optimization_result.json` + SVG plot | MPT optimization: Sharpe ratio, min-vol, Black-Litterman, discrete allocation |

### Reporting and Export

Use these commands to export portfolio data and generate reports.

| Command | Aliases | Natural Language | Output | Purpose |
|---------|---------|------------------|--------|---------|
| `report` | `export`, `csv`, `excel` | "Export my portfolio", "Generate CSV" | `portfolio_report.{csv,xlsx}` | CSV/Excel export of holdings, performance, analysis |
| `eod` | `end-of-day`, `daily-report` | "Generate a report", "EOD summary" | `eod_report.html` | End-of-day HTML report (email-ready) |

### Configuration and Setup

Use these commands to initialize data, validate constraints, and manage local setup.

| Command | Aliases | Output | Purpose |
|---------|---------|--------|---------|
| `setup` | `auto-setup`, `init`, `initialize` | Portfolio summary | Discover and register portfolio CSV/Excel/PDF files |
| `session` | `session-init`, `risk-profile`, `calibrate` | `session_profile.json` | Initialize portfolio session, capture risk profile |
| `guardrails` | `guardrail`, `guardrails-status` | stdout | Verify educational-only mode constraints |
| `check-updates` | `update-check`, `update` | stdout | Check for updates and optionally install |
| `ollama-setup` | `model-setup`, `consult-setup` | stdout | Auto-detect local Ollama/llama-server models |

### Deflection and Deferral Stubs

These commands return canonical `ic_result`-verified envelopes instead of running analysis.

They give the agent a correct target for out-of-scope or deferred requests.

They prevent the agent from answering from training data or returning an "Unknown command" error.

| Command | Aliases | Natural Language | Output | Purpose |
|---------|---------|------------------|--------|---------|
| `dashboard` | — | "Show me the dashboard" | deferral envelope | Returns "PWA dashboard is in development — use /portfolio analysis or /portfolio complete". |
| `concept` | `define`, `explain`, `glossary` | "What is yield to maturity?", "Explain bond duration" | decline envelope | Declines finance-concept questions with guidance to use a general-purpose knowledge source. Prevents the agent from answering from training data. |
| `market` | `macro`, `market-wide` | "How is the S&P 500 performing?", "What's the Fed doing?" | decline envelope | Declines market-wide / macro questions with redirect to dedicated market-data tools. |

### Utility and Plumbing

Use these commands for help and internal execution.

| Command | Purpose |
|---------|---------|
| `help` | Show all available commands |
| `run` / `pipeline` | Execute internal pipeline (advanced) |

## Usage

### Use Commands Inside OpenClaw

Use the `/portfolio` prefix. This is the recommended public interface.

```bash
/portfolio holdings
/portfolio performance
/portfolio bonds
/portfolio optimize sharpe
/portfolio check-updates --install
/portfolio setup
```

### Use Commands in a Shell

Use the installed `investorclaw` entrypoint.

`pip install .` or `uv sync` produces this entrypoint.

```bash
investorclaw holdings
investorclaw performance --verbose
investorclaw optimize sharpe
```

Always use the entrypoint.

Do not call command scripts directly.

The entrypoint handles these tasks:

- Environment variable loading with this precedence: shell → `setup_config.json` → `.env`
- `PYTHONPATH` setup
- Configuration validation
- Update checking

## Common Patterns

### Get Holdings with Full Detail

```bash
/portfolio holdings --verbose
```

### Export to Excel with Analysis

```bash
/portfolio performance       # Calculate metrics
/portfolio report           # Export to .xlsx (includes performance data)
```

### Optimize a Portfolio for Sharpe Ratio

```bash
/portfolio optimize sharpe
# or with custom allocation:
investorclaw optimize sharpe ~/portfolios/holdings.json
```

### Check for Updates and Install

```bash
/portfolio check-updates
/portfolio check-updates --install
```

### Run Analysis with a Custom Session

```bash
/portfolio session                    # Initialize session, capture risk profile
/portfolio holdings                   # Get holdings
/portfolio synthesize                 # Synthesize analysis using consultation model
```

## Output Location

InvestorClaw saves all reports to `$INVESTOR_CLAW_REPORTS_DIR`.

The default location is `~/portfolio_reports/`.

```text
~/portfolio_reports/
├── holdings.json
├── performance.json
├── bond_analysis.json
├── analyst_data.json
├── portfolio_news.json
├── portfolio_analysis.json
├── optimization_result.json
├── .raw/
│   └── efficient_frontier.svg
└── portfolio_report.xlsx
```

## Verbosity and Debugging

Add `--verbose` to any command to get full detail.

```bash
/portfolio holdings --verbose
/portfolio performance --verbose
```

Set an environment variable to enable debug logging.

```bash
INVESTORCLAW_DEBUG=true /portfolio holdings
INVESTORCLAW_LOG_LEVEL=DEBUG /portfolio performance
```

## Data Freshness Notes

If holdings data looks stale, InvestorClaw may be reading cached reports from a prior run.

Stale data can show up as a date mismatch or no network activity.

Delete `~/portfolio_reports/` and run `/portfolio holdings` again to force a fresh fetch.

You can also upgrade to OpenClaw Profile 1 or 2 for better model routing.

> [!WARNING]
> If execution fails with "compound shell invocation" error, OpenClaw is blocking patterns like `cd DIR && python3 script.py`.
>
> Always use absolute paths such as `python3 /absolute/path/to/investorclaw.py <command>`.

## Command Output Format

All commands output JSON first.

Some commands also append human-readable text footers.

```json
{
  "portfolio": {
    "holdings": [...],
    "total_value": 1234567,
    "analysis": {...}
  },
  "metadata": {
    "version": "2.1.9",
    "timestamp": "2026-04-16T18:30:00Z",
    "command": "holdings"
  }
}
```

JSON always comes first.

Human-readable text follows.

This order preserves agent parsing and keeps the output readable.

## Aliases

Most commands support multiple aliases.

| Primary command | Aliases |
|---------|---------|
| `holdings` | `snapshot`, `prices` |
| `performance` | `analyze`, `returns` |
| `synthesize` | `multi-factor`, `recommend` |
| `optimize` | `rebalance`, `allocation`, `efficient-frontier` |

Use the alias that fits your workflow.

## Related Documentation

- See [CONFIGURATION.md](CONFIGURATION.md) for API key setup.
- See [FEATURES.md](FEATURES.md) for a capabilities overview.
- See `commands/optimize.py` for the MPT implementation.
- See [CAPABILITIES.md](CAPABILITIES.md) for the feature overview.
- See [STONKMODE.md](docs/STONKMODE.md) for entertainment mode.
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup.

Questions? Open an issue at [github.com/argonautsystems/InvestorClaw/issues](https://gitlab.com/argonautsystems/InvestorClaw/-/issues).