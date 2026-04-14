# InvestorClaw

<p align="center">
  <img src="https://raw.githubusercontent.com/perlowja/InvestorClaw/main/assets/investorclaw-logo.png" alt="InvestorClaw Logo" width="200"/>
</p>

Portfolio analysis and market intelligence skill for OpenClaw. **v1.0.0** | FINOS CDM 5.x | MIT License

> **Naming note**: the package id is `investorclaw`. The OpenClaw invocation command is `/portfolio`.

---

## TL;DR

InvestorClaw is an OpenClaw skill with two modes:

1. **Personal portfolio analysis** — reads broker CSV exports, runs holdings/performance/bond pipelines, and answers follow-up questions in a persistent session.
2. **Market data tool** — queries live prices, analyst ratings, news, and yield-curve analytics for arbitrary tickers, without portfolio files.

Both modes enforce educational-only output via always-on guardrails.

- Fetches live quotes (Finnhub → Massive → Alpha Vantage → yfinance), analyst consensus, news, and optional local LLM synthesis (tier-3 enrichment).
- Does **not** execute trades, replace a broker portal, or give investment advice.
- No API keys required to start — falls back to `yfinance` automatically.
- Time to first report: ~5 minutes from `git clone` on an existing OpenClaw install.

---

## Quick Install

> **ClawHub marketplace listing is in progress.** Until then, install from GitHub.

### Ask your agent

> Install InvestorClaw from https://github.com/perlowja/InvestorClaw.git

The agent will clone, register, install Python deps, and restart the gateway.

### Manual

```bash
git clone https://github.com/perlowja/InvestorClaw.git ~/Projects/InvestorClaw
pip install -r ~/Projects/InvestorClaw/requirements.txt
openclaw plugins install --link ~/Projects/InvestorClaw
cp ~/Projects/InvestorClaw/.env.example ~/Projects/InvestorClaw/.env
# Edit .env — add FINNHUB_KEY at minimum
python3 ~/Projects/InvestorClaw/investorclaw.py setup
openclaw gateway restart
```

```bash
# Verify
openclaw plugins inspect investorclaw
python3 ~/Projects/InvestorClaw/tests_smoke.py
```

> **Important after every fresh clone**: copy your `.env` to the workspace:
> ```bash
> cp ~/Projects/InvestorClaw/.env ~/.openclaw/workspace/skills/investorclaw/.env
> ```
> Without this, the background enricher process (detached subprocess) will not pick up your API keys or consultation endpoint config.

---

## Quick Start

```bash
python3 investorclaw.py setup         # first-time portfolio file discovery
python3 investorclaw.py holdings      # holdings snapshot with live prices
python3 investorclaw.py performance   # performance analysis
python3 investorclaw.py bonds         # bond analytics (YTM, duration, FRED benchmarks)
python3 investorclaw.py help          # show all commands
```

Always invoke via the entry point — never call command scripts directly.

---

## Commands

| Command | Aliases | Primary artifact |
|---------|---------|------------------|
| `holdings` | `snapshot`, `prices` | `holdings.json` |
| `performance` | `analyze`, `returns` | `performance.json` |
| `bonds` | `bond-analysis`, `analyze-bonds` | `bond_analysis.json` |
| `analyst` | `analysts`, `ratings` | `analyst_data.json` |
| `news` | `sentiment` | `portfolio_news.json` |
| `analysis` | `portfolio-analysis` | `portfolio_analysis.json` |
| `synthesize` | `multi-factor`, `recommend` | `portfolio_analysis.json` |
| `fixed-income` | `fixed-income-analysis` | `fixed_income_analysis.json` |
| `report` | `export`, `csv`, `excel` | `portfolio_report.{csv,xlsx}` |
| `eod` | `end-of-day`, `daily-report` | `eod_report.html` |
| `session` | `session-init`, `risk-profile` | `session_profile.json` |
| `lookup` | `query`, `detail` | stdout |
| `guardrails` | `guardrail`, `guardrails-status` | stdout |
| `run` | `pipeline` | pipeline stdout + artifacts |
| `ollama-setup` | `model-setup`, `consult-setup` | stdout |
| `setup` | `auto-setup`, `init` | setup output |

Output files go to `$INVESTOR_CLAW_REPORTS_DIR` (default: `~/portfolio_reports/`). Add `--verbose` to any command for full detail.

---

## Model All-Stars

Best performers across synthesis quality, speed, guardrail compliance, and zero hallucinations (QC8=0 across all passing runs). Full benchmark data: [MODELS.md](MODELS.md).

### Hybrid (consultation + operational LLM)

| Rank | Configuration | QC4 | QC5 | Speed | Notes |
|------|--------------|:---:|:---:|:-----:|-------|
| 🥇 | `xai/grok-4-1-fast` + `gemma4-consult` | 113 | 1,184 words | ~65 tok/s (local) | **Canonical best.** 14× metric density vs cloud baseline. HMAC fingerprint chain, verbatim attribution, is_heuristic=false. WF39. |
| 🥈 | `together/moonshotai/Kimi-K2.5` + `gemma4-consult` | 18 | 350 words | ~65 tok/s (local) | Hybrid confirmed (215 SVG cards). Narrative synthesis style vs Grok's data-table density. WF71. |

### Single-model (cloud-only)

| Rank | Model | QC4 | QC5 | Speed | Notes |
|------|-------|:---:|:---:|:-----:|-------|
| 🥇 | `together/deepseek-ai/DeepSeek-V3.1` | 35+ | 400 words | Together AI | **Top single-model.** Best synthesis density without enrichment. QC8=0. WF68. |
| 🥈 | `together/moonshotai/Kimi-K2.5` | 40+ | 250 words | Together AI | Highest metric citation count. Strong analyst coverage prose. QC8=0. WF66. |
| 🥉 | `groq/moonshotai/kimi-k2-instruct-0905` | ~20 | ~350 words | ~800 tok/s | Best Groq prose quality. ⚠️ Preview tier only — may be discontinued. WF58. |
| | `groq/openai/gpt-oss-120b` | ~10 | ~280 words | ~500 tok/s | **Best production-stable Groq option.** $0.15/$0.60/M. WF46. |
| | `groq/openai/gpt-oss-20b` | ~8 | ~250 words | ~1000 tok/s | Fastest option. $0.075/$0.30/M. WF59. |
| | `openai/gpt-5.4` | — | — | OpenAI | PASS, 272K context (smallest frontier). WF63. |
| | `google/gemini-3.1-pro-preview` | 17 | 104 words | Google | Thin synthesis; 1M context. WF65. |

### Guardrails & hallucination score

All passing models scored **QC8=0** (zero fabricated portfolio facts across W1–W8). The notable exception is `groq/qwen/qwen3-32b` (DEGRADED, WF67) — W7 generated specific put option and trailing-stop recommendations without educational framing, violating the educational-only guardrail.

---

## Config Profiles

### Profile 1 — Hybrid (recommended)

**Operational LLM**: `xai/grok-4-1-fast`  
**Consultation model**: `gemma4-consult` via local Ollama (~10 GB VRAM)

Designed for portfolios with individual equities. The local consultation model enriches per-symbol analyst records before synthesis runs — the harness measured **14× more metric citations** vs cloud-only baseline. Adds HMAC fingerprint chain and verbatim attribution controls.

OpenClaw config:
```json
{ "agents": { "defaults": { "model": { "primary": "xai/grok-4-1-fast" } } } }
```

`.env`:
```bash
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
```

> `xai/grok-4-1-fast` requires `/portfolio update-identity` at the start of each session for full guardrail disclaimer compliance.

---

### Profile 2 — Cloud-only

**Operational LLM**: `xai/grok-4-1-fast` (or any frontier model for specific sessions)

Best for ETF-heavy portfolios where per-holding analyst enrichment adds little value. Cloud-only synthesis quality for allocation, bond analytics, and sector breakdown is good. For complex portfolios with many individual equity positions, synthesis will be shallower — see [MODELS.md](MODELS.md) for measured density scores.

OpenClaw config:
```json
{ "agents": { "defaults": { "model": { "primary": "xai/grok-4-1-fast" } } } }
```

No `.env` consultation keys needed. Use a premium frontier model for specific high-value sessions:
```bash
openclaw models set together/deepseek-ai/DeepSeek-V3.1   # top single-model synthesis (QC5≈400 words)
openclaw models set together/moonshotai/Kimi-K2.5         # strong non-frontier alternative (QC5≈250 words)
openclaw models set groq/openai/gpt-oss-120b              # fastest/cheapest option (Groq, 128K ctx)
```

> `xai/grok-4.20-0309-non-reasoning` was tested (WF64) and is **not recommended** — W4 and W5 standalone tool payloads are rejected; W6 synthesize works by running those pipelines inline but the split workflow is unreliable.

---

### Profile 3 — Budget / fast (Groq)

**Operational LLM**: `groq/openai/gpt-oss-120b` or `groq/openai/gpt-oss-20b`

500–1000 tok/s. 128K context limits to small-medium portfolios. Best for quick single-session queries where cost or speed matters. Not suitable for large fully-enriched sessions.

```json
{ "agents": { "defaults": { "model": { "primary": "groq/openai/gpt-oss-120b" } } } }
```

---

## Consultation Artifact Format

Control what artifact is written per enriched symbol via `INVESTORCLAW_CARD_FORMAT` (default `both`):

| Value | Artifact | Notes |
|-------|----------|-------|
| `json` | `~/.investorclaw/quotes/{SYMBOL}.quote.json` | HMAC fingerprint, synthesis text, attribution. Mobile-safe; no `INVESTOR_CLAW_REPORTS_DIR` needed. Safe for WhatsApp, Signal, Telegram. |
| `svg` | `{REPORTS_DIR}/.raw/consultation_cards/{SYMBOL}.svg` | Visual card with fingerprint badge. Requires `INVESTOR_CLAW_REPORTS_DIR`. |
| `both` | Both of the above | Default for desktop/web sessions. |

The `json` artifact is always machine-readable and persists independently of the SVG renderer.

---

## Data Providers

| Provider | Quotes | History | News | Analyst | Free tier |
|----------|:------:|:-------:|:----:|:-------:|-----------|
| **yfinance** | ✅ | ✅ | ✅ | ✅ | Unlimited — no key |
| **Finnhub** | ✅ fast | ❌ 403 free | ✅ | ⚠️ unreliable free | 60 req/min |
| **Massive** | ✅ batch 268ms | ✅ full OHLCV | ✅ | ❌ | Prev-day only (paid recommended) |
| **Alpha Vantage** | ✅ sequential | ✅ adjusted EOD | ❌ | ✅ earnings proxy | 25 req/day |
| **NewsAPI** | ❌ | ❌ | ✅ | ❌ | 100 req/day |

**Quick config options:**

```bash
# Zero-cost start
INVESTORCLAW_PRICE_PROVIDER=yfinance

# Free with keys (better reliability)
INVESTORCLAW_PRICE_PROVIDER=auto
INVESTORCLAW_FALLBACK_CHAIN=finnhub,alpha_vantage,yfinance
FINNHUB_KEY=...   ALPHA_VANTAGE_KEY=...   NEWSAPI_KEY=...

# Recommended for regular use
INVESTORCLAW_PRICE_PROVIDER=massive
MASSIVE_API_KEY=...   FINNHUB_KEY=...
```

---

## Local Consultation Setup (Optional, Strongly Recommended)

The consultation layer enriches per-symbol analyst data locally before the cloud operational model sees the result. This is the primary driver of information density — not model capability.

```bash
# .env
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

Create the tuned model:
```bash
ollama create gemma4-consult -f docs/gemma4-consult.Modelfile
```

**Hardware**: ~10 GB VRAM (RTX 3080 class or better, CUDA 8.0+, or Mac 16 GB unified memory). Ollama >= 0.20.x.

Run `/portfolio ollama-setup` to auto-detect available models on your endpoint.

---

## EOD Report

The `eod` command generates an HTML email report summarizing your portfolio at end-of-day.

```bash
python3 investorclaw.py eod --via-gog --email-to you@gmail.com   # Google CLI
python3 investorclaw.py eod --email-to you@example.com            # SMTP
python3 investorclaw.py eod --no-email                            # file only
```

![InvestorClaw EOD report — synthetic portfolio sample](assets/eod-report-sample.png)

Install scheduled delivery:
```bash
python3 eod_scheduler.py --install
```

---

## Privacy and Security

- **PII scrubbing**: credit card numbers, SSNs, and account IDs are redacted from CSV columns on load
- **Prompt injection defense**: portfolio text columns are scanned before passing to any LLM
- **Math verification**: all financial calculations are deterministic Python — the LLM never does portfolio math
- **Data locality**: raw CSV data is never sent to external APIs; only computed summaries reach the cloud operational model
- **Guardrails**: `data/guardrails.yaml` enforces educational-only output, blocks suitability assessments

With consultation enabled, structured synthesis runs locally first. The cloud model sees only compact downstream artifacts and quoted consultative output.

---

## Requirements

- Python 3.9+
- OpenClaw >= 2026.4.x
- Optional API keys (all have free tiers): Finnhub, Alpha Vantage, Massive, NewsAPI, FRED
- Without keys: falls back to `yfinance`

### Tested environment

| Role | System |
|------|--------|
| Developer workstation | macOS 26.5, Apple M1 Max 10c, 32 GB, Python 3.14.3, OpenClaw 2026.4.9 |
| Inference host | Debian 13, AMD Threadripper PRO 5945WX 12c, 128 GB, RTX 4500 Ada 24 GB VRAM, Ollama 0.20.3 |

---

## Tested Models

Full model testing results, hybrid vs single-model mode definitions, harness benchmark scores, Groq catalog, Together AI compatibility matrix, and blocked models are documented in **[MODELS.md](MODELS.md)**.

---

## Repository Layout

| Path | Purpose |
|------|---------|
| `investorclaw.py` | Entry point, bootstrap, routing, guardrail priming |
| `commands/` | One command script per feature |
| `config/` | Config loading, arg synthesis, path resolution, help text |
| `models/` | Portfolio, holdings, routing, and context models |
| `providers/` | Market and symbol data providers |
| `rendering/` | Compact serializers, consultation cards, disclaimers, progress |
| `runtime/` | Router, environment bootstrap, subprocess execution |
| `services/` | Consultation policy, portfolio consolidation, PDF extraction |
| `setup/` | First-run, installer, setup wizard, identity updater |
| `internal/` | Tier-3 enrichment internals |
| `data/` | Guardrails and symbol/reference data |
| `tests/` | Unit and contract tests |
| `pipeline.py` | Full pipeline entry |
| `investorclaw_harness_v612.txt` | Test harness |
| `MODELS.md` | Full model testing catalog and benchmark results |

**Never committed**: `.env`, `~/portfolios/*`, `~/portfolio_reports/`

---

## Design Intent

InvestorClaw is a reference design for a **data-intensive, stateful agentic skill**. It demonstrates compact agent-facing outputs with raw artifact preservation, deterministic downstream processing, optional local consultative LLMs, financial guardrails, and multi-step setup and report-generation flows.

The enrichment layer (`internal/tier3_enrichment.py`) is the primary driver of synthesis quality — not the operational model. Switching from heuristic to enriched mode produces a 10–15× step-change in information density. Switching operational models has modest effect by comparison.

---

## Compliance

**NOT INVESTMENT ADVICE.** InvestorClaw provides educational portfolio analysis only. It is not a substitute for professional financial advice and does not assess personal risk tolerance, goals, or investment suitability.

---

## Changelog

**v1.0.0 (2026-04-14)**
- Phase 5 clean benchmark complete: all 9 DEV-001-contaminated runs (WF36–WF41, WF48, WF53–WF55) re-validated in IC-RUN-20260413-010 (WF63–WF71). Full results in [MODELS.md](MODELS.md).
- Confirmed new passing models: DeepSeek-V3.1, Kimi-K2.5 (hybrid), Gemini-3.1-pro-preview, GPT-5.4, MiniMax-M2.7, GLM-5.
- Degraded: grok-4.20-0309-non-reasoning (W4/W5 tool payload rejection), qwen3-32b (update-identity unrecognized, W7 guardrail issue).
- Session cleanup now part of post-harness RESET protocol.

## License

MIT — see [LICENSE](LICENSE).
