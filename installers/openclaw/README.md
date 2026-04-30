# InvestorClaw for OpenClaw

**OpenClaw Skill Installation & Configuration**

v2.5.0 | Apache 2.0 Dual License | Educational Use Only

---

## What Is This?

This directory contains InvestorClaw's **OpenClaw skill manifest and installer**.

If you're looking for:
- **Claude Code plugin**: install from the [InvestorClaude](https://gitlab.com/argonautsystems/InvestorClaude) repo (separate marketplace); see root `README.md`
- **Standalone Python CLI**: See root `README.md` (Advanced section)
- **OpenClaw skill** (this): Keep reading

---

## Install InvestorClaw as an OpenClaw Skill

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
```

This installs InvestorClaw to `~/.openclaw/workspace/skills/investorclaw/` and sets up the skill configuration.

**What gets installed:**
- InvestorClaw adapter package
- `ic-engine` and `clio` dependencies via `uv sync`
- Skill-local `.env` configuration file
- Portfolio directory

---

## Use After Installation

```bash
# Using openclaw CLI
openclaw agent -m "/portfolio ask \"What's in my portfolio?\""
openclaw agent -m "/portfolio ask \"How am I doing?\""
openclaw agent -m "/portfolio refresh"
```

---

## Configuration

Edit `~/.openclaw/workspace/skills/investorclaw/.env` to:
- Add API keys (Finnhub, NewsAPI, etc.)
- Configure operational models
- Set portfolio directory

See root `README.md` and `CONFIGURATION.md` for full configuration options.

---

## Adapter Shape

InvestorClaw v2.5.0 is an adapter package for OpenClaw and related runtimes.
The Python analysis engine is provided by `ic-engine`; this repo provides the
OpenClaw manifest, installer, routing contract, and `investorclaw` shim.
The user-facing surface is `portfolio_ask` / `investorclaw ask` plus
`portfolio_refresh` / `investorclaw refresh`.

Claude Code plugin code lives in [InvestorClaude](https://gitlab.com/argonautsystems/InvestorClaude) — install from that repo's marketplace, not this one.
