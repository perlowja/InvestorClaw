# OpenClaw — InvestorClaw Installation & Configuration

Deploy InvestorClaw as an **OpenClaw skill** on Linux/macOS workstations and servers.

---

## Quick Start (5 minutes)

### 1. Install InvestorClaw

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
```

Installer creates: `~/.openclaw/workspace/skills/investorclaw/`

### 2. Verify Installation

```bash
openclaw agent -m "investorclaw ask \"What's in my portfolio?\""
```

You should see a deterministic InvestorClaw portfolio answer.

### 3. Upload Your Portfolio

```bash
openclaw agent -m "analyze my portfolio
[portfolio.csv attached]"
```

OpenClaw will analyze your holdings and provide a summary.

---

## What You Get

- ✅ Two-command deterministic surface: `ask` and `refresh`
- ✅ Skill manifest in `openclaw/skill.json`
- ✅ Full automation via OpenClaw agent
- ✅ Local inference support (Ollama, vLLM)
- ✅ Environment-based configuration

---

## Configuration

Edit `~/.openclaw/workspace/skills/investorclaw/.env` to set:

```bash
# Operational model (default: xAI Grok 4.1 Fast Reasoning)
OPERATIONAL_LLM=xai/grok-4-1-fast-reasoning

# Market data APIs (optional)
FINNHUB_KEY=your_key_here
NEWSAPI_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Local inference (optional)
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
INVESTORCLAW_CONSULTATION_MODEL=hermes3:8b-q4_K_M
```

Restart OpenClaw agent after changes.

---

## Commands

The v2.5.0 InvestorClaw surface is:

```bash
openclaw agent -m "investorclaw ask \"<question>\""
openclaw agent -m "investorclaw refresh"
```

Examples:
- `investorclaw ask "What's in my portfolio?"` — portfolio snapshot
- `investorclaw ask "How am I doing?"` — returns and metrics
- `investorclaw ask "Show my bond exposure"` — bond analysis
- `investorclaw ask "How should I rebalance?"` — rebalancing analysis
- `investorclaw refresh` — force fresh prices/news/cache

See `openclaw/skill.json` for the command list.

---

## Troubleshooting

**Command not found**: Restart OpenClaw agent after editing `.env`

**Network error**: Check API keys (FINNHUB_KEY, NEWSAPI_KEY, etc.) or verify internet connection

**Local LLM not connecting**: Ensure Ollama is running (`ollama serve`) and accessible at `http://localhost:11434`

---

## Learn More

- **[Architecture & Comparison](../shared/PLATFORM_COMPARISON.md)** — How OpenClaw differs from ZeroClaw and Hermes Agent
- **[Feature Matrix](../shared/FEATURE_MATRIX.md)** — Command support across platforms
- **[Local Inference Setup](../shared/LOCAL_INFERENCE_GUIDE.md)** — Setting up Ollama for offline analysis
- **[OpenClaw Official Docs](https://github.com/openclaw/openclaw)** — Full agent documentation

---

**Next**: 
- **Other Claw platforms?** → [Claw Home](../README.md)
- **Claude Code?** → [Claude Documentation](../../claude/README.md)
