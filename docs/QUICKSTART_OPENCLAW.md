# InvestorClaw — OpenClaw Quick Start Guide

**v2.5.0** | Installation & First Run for OpenClaw | ~5 minutes

## What is OpenClaw?

OpenClaw is a **lightweight agent runtime** that runs InvestorClaw as a skill-based system. Choose OpenClaw if you:

- ✅ Already use OpenClaw for other agents
- ✅ Want flexible LLM provider selection (Together.ai, Groq, OpenAI, local)
- ✅ Need on-premises deployment control
- ✅ Prefer CLI-based portfolio analysis

**Not for you if**: You want Claude Code's interactive dashboards or conversational Q&A in one chat.

---

## ⚠️ Important Disclaimer

**InvestorClaw is an EDUCATIONAL portfolio analysis tool.** It is:
- ❌ NOT a fiduciary advisor
- ❌ NOT providing investment advice
- ✅ Designed to help you have informed conversations with your financial advisor

**Always consult a qualified financial professional before making investment decisions.**

---

## Quick Start (5 minutes)

### Step 1: Install InvestorClaw Skill

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
```

The installer automatically:
- ✅ Clones InvestorClaw to `~/.openclaw/workspace/skills/investorclaw`
- ✅ Creates `.env` configuration with API key prompts
- ✅ Creates `~/portfolios/` directory for holdings files
- ✅ Verifies OpenClaw CLI is installed

**Time**: ~2 minutes on standard broadband

### Step 2: Configure LLM Provider (Optional)

The install script prompts for LLM configuration. Choose one:

**Recommended: Together.ai**
```bash
/portfolio llm-config
# Select: "together" (or "groq", "openai", "local")
# Paste API key when prompted
```

Or skip and use defaults (xAI Grok-4 via OpenClaw).

### Step 3: Add Portfolio

Export holdings from your broker and save to `~/portfolios/`:

```bash
# Copy your broker CSV
cp ~/Downloads/MyHoldings.csv ~/portfolios/

# Or use the sample
cp docs/samples/sample_portfolio.csv ~/portfolios/
```

### Step 4: Run Your First Command

```bash
# First-time setup / portfolio discovery
/portfolio ask "Set up InvestorClaw and detect my portfolio files"

# Natural-language analysis
/portfolio ask "What's in my portfolio?"
/portfolio ask "How am I doing?"
/portfolio ask "Show my bond exposure"

# Fresh prices/news/cache
/portfolio refresh
```

---

## Primary Commands

The v2.5.0 adapter surface has two commands:

```bash
/portfolio ask "<question>"       # Any portfolio or finance question
/portfolio refresh                # Force a fresh deterministic run
```

---

## Backend Commands

Historical backend commands are retained behind `investorclaw ask`, but users should not pick them directly.

---

## Configuration

### `.env` File Location

```bash
~/.investorclaw/.env
```

### Key Settings

```bash
# Narrative (cloud synthesis) provider
INVESTORCLAW_NARRATIVE_PROVIDER=together
INVESTORCLAW_NARRATIVE_API_KEY=your-key-here

# Optional: Consultative (refinement) LLM
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult

# Data API keys (all optional, falls back to yfinance)
FINNHUB_KEY=...
NEWSAPI_KEY=...
POLYGON_API_KEY=...
```

### Interactive Setup

```bash
/portfolio llm-config
```

Guided wizard for provider selection (Together.ai, Groq, OpenAI, local Ollama, or disabled).

---

## Natural Language Queries

You don't need to memorize commands. Ask the agent in plain English:

| Ask this... | Command |
|---|---|
| "What's in my portfolio?" | holdings |
| "How am I doing?" | performance |
| "What's my bond exposure?" | bonds |
| "Analyze my portfolio" | synthesize |
| "How should I rebalance?" | optimize |
| "Any news on my stocks?" | news |
| "What does Wall Street think?" | analyst |
| "Tell me about NVDA" | lookup --symbol NVDA |

---

## Data Sources & Optional APIs

All data sources are **optional**. Falls back to yfinance (free, unlimited):

| Source | Key Name | Free Tier | Purpose |
|---|---|---|---|
| yfinance | (none) | Unlimited | Default: live quotes |
| Finnhub | FINNHUB_KEY | 60 req/min | Analyst ratings |
| NewsAPI | NEWSAPI_KEY | 100 req/day | Portfolio news |
| Polygon/Massive | POLYGON_API_KEY | Paid | Premium real-time data |
| Alpha Vantage | ALPHA_VANTAGE_KEY | 25 req/day | EOD + earnings |
| FRED | (none) | 120 req/min | Treasury benchmarks |

Get free keys at:
- Finnhub: https://finnhub.io
- NewsAPI: https://newsapi.org
- Alpha Vantage: https://www.alphavantage.co

---

## Troubleshooting

### "portfolio: command not found"

OpenClaw not running or skill not loaded. Check:
```bash
# Verify OpenClaw is running
ps aux | grep openclaw

# If not, start it
openclaw agent -m "help"
```

### "Portfolio not found"

Ask InvestorClaw to discover your holdings:
```bash
/portfolio ask "Set up InvestorClaw and detect my portfolio files"
```

Place CSV files in `~/portfolios/` first.

### "No API keys configured"

Optional — falls back to yfinance. To add keys:
```bash
/portfolio llm-config
```

### Slow responses

Check your LLM provider:
- Together.ai/Groq: usually ~2-3 seconds
- Local Ollama: ~5-10 seconds (depends on hardware)
- OpenAI: ~1-2 seconds (if configured)

---

## Comparison with Other Platforms

| Feature | OpenClaw | Claude Code | ZeroClaw | Hermes Agent |
|---|---|---|---|---|
| **Cost** | Free (cloud optional) | $0.05–$2/mo | Free | Free |
| **Setup** | 2 min | 1 min | 10 min | 5 min |
| **LLM Choice** | ✅ Flexible | Claude only | Groq default | Local only |
| **Privacy** | Optional local | Cloud | Local | Local |
| **Speed** | Fast (cloud) | Very fast | Moderate | Slow (CPU) |
| **Context** | Configurable | 1M | 4K–32K | 4K–32K |
| **Offline** | ✅ Optional | ❌ Needs API | ✅ Full | ✅ Full |
| **Dashboard** | ❌ CLI only | ✅ PWA | ❌ CLI | ❌ CLI |

**Best for**: Flexibility + control + integration with other OpenClaw agents.

---

## Sample Portfolio

A sample 50-position portfolio is included for testing:

```bash
cp docs/samples/sample_portfolio.csv ~/portfolios/
/portfolio ask "Set up InvestorClaw and detect my portfolio files"
/portfolio ask "What's in my portfolio?"
```

Takes ~5 seconds to fetch live quotes, calculate concentration, and display.

---

## Local Inference (Optional Hybrid Mode)

Run Ollama locally for consultative enrichment:

```bash
# 1. Install Ollama
brew install ollama

# 2. Start daemon
ollama serve &

# 3. Pull model
ollama pull gemma4-consult

# 4. Configure InvestorClaw
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
export INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

Now analysis uses cloud narrative + local consultative enrichment for maximum privacy.

---

## What's Next?

- **Command surface**: `investorclaw ask` and `investorclaw refresh`
- **Configuration**: See [CONFIGURATION.md](../CONFIGURATION.md)
- **Architecture**: See [docs/PLATFORM_COMPARISON.md](../docs/claw/shared/PLATFORM_COMPARISON.md)
- **Stonkmode**: See [docs/STONKMODE.md](../docs/STONKMODE.md)
- **Local inference**: See [docs/LOCAL_INFERENCE_GUIDE.md](../docs/claw/shared/LOCAL_INFERENCE_GUIDE.md)

---

## Troubleshooting Checklist

✅ OpenClaw installed? → `openclaw --version`
✅ Portfolio file in `~/portfolios/`? → `ls ~/portfolios/`
✅ `.env` configured? → `cat ~/.investorclaw/.env | grep INVESTORCLAW_NARRATIVE`
✅ LLM provider working? → Run `/portfolio ask "What's in my portfolio?"`

---

**Questions?** Open an issue: https://gitlab.com/argonautsystems/InvestorClaw/-/issues

**Last Updated**: 2026-04-21  
**Status**: v2.1.0-dev, Production-Ready OpenClaw Integration
