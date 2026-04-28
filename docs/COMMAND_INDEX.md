# Command Index

Complete list of InvestorClaw commands with invocation syntax for both Claude Code and OpenClaw.

---

## Analysis Commands

### Holdings Snapshot

**Purpose:** What you own, current prices, concentration analysis

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-holdings` |
| OpenClaw | `/portfolio holdings` |

**Example:**
```
/investorclaw:ic-holdings
# Output: Current holdings with live prices, unrealized gains, sector breakdown
```

---

### Performance Metrics

**Purpose:** Returns, Sharpe ratio, beta, max drawdown, recovery analysis

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-performance` |
| OpenClaw | `/portfolio performance` |

**Example:**
```
/investorclaw:ic-performance
# Output: YTD return, Sharpe ratio (vs. S&P 500), volatility, drawdown chart
```

---

### Bond Analytics

**Purpose:** Yield-to-maturity (YTM), duration, credit quality, maturity ladder

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-bonds` |
| OpenClaw | `/portfolio bonds` |

**Example:**
```
/investorclaw:ic-bonds
# Output: Bond-by-bond YTM, weighted avg duration, credit rating distribution, ladder chart
```

---

### Analyst Consensus

**Purpose:** Wall Street ratings (Buy/Hold/Sell) and price targets for your holdings

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-analyst` |
| OpenClaw | `/portfolio analyst` |

**Example:**
```
/investorclaw:ic-analyst
# Output: Consensus rating per holding, 12-month price targets, analyst count
```

---

### News & Sentiment

**Purpose:** Recent headlines + sentiment correlation for portfolio holdings

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-news` |
| OpenClaw | `/portfolio news` |

**Example:**
```
/investorclaw:ic-news
# Output: Recent headlines for AAPL, MSFT, etc. + sentiment (bullish/bearish)
```

---

### Multi-Factor Analysis

**Purpose:** Combines holdings, performance, bonds, analyst, and news into synthesized insights

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-synthesize` |
| OpenClaw | `/portfolio synthesize` |

**Example:**
```
/investorclaw:ic-synthesize
# Output: "Your portfolio is 65% equity (concentrated in tech), 25% bonds (short duration), 10% cash"
```

---

### Portfolio Optimization

**Purpose:** Rebalancing suggestions (educational only, no trades executed)

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-optimize` |
| OpenClaw | `/portfolio allocation` or `/portfolio optimize` |

**Example:**
```
/investorclaw:ic-optimize
# Output: "Your tech weighting is 45% vs. 25% benchmark. Consider rebalancing to healthcare (underweight)."
```

---

### Single-Ticker Deep Dive

**Purpose:** Detailed analysis of one holding (technical, fundamental, sentiment)

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-lookup SYMBOL` |
| OpenClaw | `/portfolio lookup SYMBOL` |

**Example:**
```
/investorclaw:ic-lookup NVDA
# Output: NVDA fundamentals, technicals, analyst consensus, related news
```

---

## Reporting Commands

### Export Holdings & Metrics

**Purpose:** CSV or Excel export of holdings with performance metrics

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-report` |
| OpenClaw | `/portfolio export` or `/portfolio report` |

**Example:**
```
/investorclaw:ic-report
# Output: CSV file with holdings, current price, unrealized G/L, allocation %
```

---

### End-of-Day HTML Report

**Purpose:** Daily portfolio summary (email-ready HTML, dark theme, mobile-responsive)

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-eod-report` |
| OpenClaw | `/portfolio eod` |

**With email:**
```
/investorclaw:ic-eod-report --email you@example.com
# Output: HTML report emailed to you@example.com
```

---

## Setup & Configuration

### Initial Setup

**Purpose:** Discover portfolio files, auto-detect broker format, consolidate multiple files

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-setup` |
| OpenClaw | `/portfolio setup` |

**Example:**
```
/investorclaw:ic-setup
# Interactive wizard: scans ~/portfolios/, detects Schwab/Fidelity/Vanguard/UBS formats
```

---

### LLM Configuration

**Purpose:** Optional setup of verification layer (Claude Code) or narrative provider (OpenClaw)

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-llm-config` |
| OpenClaw | `/portfolio llm-config` |

**Claude Code:** Enables subagent verification for audit trails  
**OpenClaw:** Configures LLM provider (Ollama, Together.ai, Groq, NGC, custom, or disabled)

---

### Session Initialization

**Purpose:** Set risk profile, investment goals, advisor mode (professional vs. individual)

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-session` |
| OpenClaw | `/portfolio session` |

**Example:**
```
/investorclaw:ic-session
# Sets investor risk profile, guardrail strictness, output format
```

---

### Check for Updates

**Purpose:** Verify installed version matches latest release

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-check-updates` |
| OpenClaw | `/portfolio check-updates` or `/portfolio update` |

**Example:**
```
/investorclaw:ic-check-updates
# Output: "v2.0.0 installed. Latest is v2.0.0. Up to date."
```

---

## Optional/Advanced Commands

### Interactive Dashboard

**Purpose:** Live Plotly charts with pie, sectors, sparklines, bond ladder, rebalancing simulator (Claude Code only)

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-dashboard` |
| OpenClaw | ❌ Not supported |

**Example:**
```
/investorclaw:ic-dashboard
# Renders interactive HTML artifact in Claude Code
```

---

### Stonkmode (Entertainment)

**Purpose:** Comic narration by 30 fictional finance TV personalities

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-stonkmode` |
| OpenClaw | `/portfolio stonkmode` |

**Example:**
```
/investorclaw:ic-stonkmode
# Output: "And now, with your portfolio sitting pretty at +8.3%, here's Dr. Stonk..."
```

---

### Guardrails Status

**Purpose:** Verify educational-only constraints are enforced

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-guardrails` |
| OpenClaw | `/portfolio guardrails` |

**Example:**
```
/investorclaw:ic-guardrails
# Output: "✅ Educational mode ON. Investment advice disabled."
```

---

### Help

**Purpose:** List all available commands

| Platform | Command |
|----------|---------|
| Claude Code | `/investorclaw:ic-help` |
| OpenClaw | `/portfolio help` |

**Example:**
```
/investorclaw:ic-help
# Output: Annotated list of 28 unique commands (with 94+ aliases) with short descriptions
```

---

## Invocation Patterns

### Claude Code

```bash
/investorclaw:ic-COMMAND [arguments]

Examples:
/investorclaw:ic-holdings
/investorclaw:ic-performance
/investorclaw:ic-lookup NVDA
/investorclaw:ic-report --format csv
```

### OpenClaw

```bash
/portfolio COMMAND [arguments]
# or
investorclaw COMMAND [arguments]

Examples:
/portfolio holdings
/portfolio performance
/portfolio lookup NVDA
/portfolio export --format csv
```

---

## Command Availability by Category

| Category | Claude Code | OpenClaw |
|----------|---|---|
| Analysis (7 commands) | ✅ All | ✅ All |
| Reporting (2 commands) | ✅ All | ✅ All |
| Setup (3 commands) | ✅ All | ✅ All |
| Dashboard | ✅ | ❌ |
| Entertainment | ✅ | ✅ |
| Utilities (4 commands) | ✅ All | ✅ All |
| **Total** | **28 commands (94+ aliases)** | **28 commands** |

---

## Quick Reference by Use Case

### "What do I own?"
```
Claude Code: /investorclaw:ic-holdings
OpenClaw: /portfolio holdings
```

### "How am I doing?"
```
Claude Code: /investorclaw:ic-performance
OpenClaw: /portfolio performance
```

### "Tell me about my bonds"
```
Claude Code: /investorclaw:ic-bonds
OpenClaw: /portfolio bonds
```

### "Should I rebalance?"
```
Claude Code: /investorclaw:ic-optimize
OpenClaw: /portfolio optimize
```

### "What does Wall Street think?"
```
Claude Code: /investorclaw:ic-analyst
OpenClaw: /portfolio analyst
```

### "What's the latest on my stocks?"
```
Claude Code: /investorclaw:ic-news
OpenClaw: /portfolio news
```

### "Give me everything"
```
Claude Code: /investorclaw:ic-synthesize
OpenClaw: /portfolio synthesize
```

### "Export my portfolio"
```
Claude Code: /investorclaw:ic-report
OpenClaw: /portfolio export
```

### "Email me a daily summary"
```
Claude Code: /investorclaw:ic-eod-report --email you@example.com
OpenClaw: /portfolio eod --email you@example.com
```

---

See `PLATFORM_COMPARISON.md` for feature differences. See `docs/DATA_FLOW.md` for data privacy.
