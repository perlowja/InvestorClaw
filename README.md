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

> **Data freshness**: If the agent returns holdings data without fetching live prices, it may be reading cached report files from a prior run. This happens when the agent falls through to the shell tool with a degraded model rather than routing through the plugin. Signs of stale data: the response date does not match today, or no network activity is visible during the command. To force a fresh fetch, delete `~/portfolio_reports/` and re-run `/portfolio holdings`, or upgrade to Profile 1 or 2.

> **Exec preflight**: OpenClaw blocks compound shell invocations (`cd DIR && python3 script.py`). The plugin uses absolute paths internally; if you invoke InvestorClaw scripts directly from the shell tool, use `python3 /absolute/path/to/investorclaw.py <command>` — not a `cd` prefix.

---

## Model All-Stars

Best performers across synthesis quality, speed, guardrail compliance, and zero hallucinations (QC8=0 across all passing runs). Full benchmark data: [MODELS.md](MODELS.md).

### Hybrid (consultation + operational LLM)

| Rank | Configuration | QC3 | QC4 | QC5 | Notes |
|------|--------------|:---:|:---:|:---:|-------|
| 🥇 | `xai/grok-4-1-fast` + `gemma4-consult` | 8 | 113 | 1,184 words | **Canonical best.** 19× metric density vs cloud-only. HMAC chain, is_heuristic=false. WF39. |
| 🥈 | `together/moonshotai/Kimi-K2.5` + `gemma4-consult` | 24 | 82 | 579 words | Re-benchmarked WF84: 4.6× over prior run. Full account breakdown, bond analytics, news. |
| 🥉 | `xai/grok-4.20-0309-non-reasoning` + `gemma4-consult` | 14 | 17 | ~200 words | Narrative prose; most tickers. Upgraded from DEGRADED. 1M context. WF74. |

### Single-model (cloud-only, IC-RUN-20260414-003)

| Rank | Model | QC3 | QC4 | QC5 | Notes |
|------|-------|:---:|:---:|:---:|-------|
| 🥇 | `together/MiniMaxAI/MiniMax-M2.7` | 27 | **108** | 541 words | **Top single-model overall.** Full account tables, analyst, bond detail. $0.30/$1.20/M. WF82. |
| 🥈 | `together/zai-org/GLM-5` | 20 | 74 | 481 words | Rich account breakdown. $1.00/$3.20/M. WF83. |
| 🥉 | `together/moonshotai/Kimi-K2.5` | 16 | 55 | 256 words | Strong analyst coverage prose. $0.50/$1.50/M. WF76. |
| | `google/gemini-3.1-pro-preview` | 15 | 46 | 340 words | 1M context; significant ↑ from context injection. WF80. |
| | `together/deepseek-ai/DeepSeek-V3.1` | 13 | 44 | 160 words | $0.60/$1.70/M. WF75. |
| | `openai/gpt-5.4` | 14 | 28 | 178 words | 272K context (smallest frontier). WF81. |
| | `groq/moonshotai/kimi-k2-instruct-0905` | 9 | 25 | 151 words | ⚠️ Preview tier only. WF77. |
| | `groq/openai/gpt-oss-120b` | 19 | 17 | 376 words | Production-stable Groq; verbose but low metric density. $0.15/$0.60/M. WF78. |
| 🚫 | `groq/openai/gpt-oss-20b` | — | — | — | FAIL: malformed tool calls. WF79. |
| | `xai/grok-4-1-fast` (cloud-only + injection) | 17 | 39 | 171 words | 6.5× vs pre-injection WF72; below top-tier single-model. WF85. |
| 🚫 | `xai/grok-4.20-0309-non-reasoning` (cloud-only) | — | — | — | FAIL: tool payload rejection. **Hybrid-only** (WF74 PASS in hybrid). WF86. |
| ⚠️ last | `xai/grok-4-1-fast` (cloud-only, pre-injection) | 0 | 6 | ~50 words | Pre-injection baseline. WF72. |

### Guardrails & hallucination score

All passing models scored **QC8=0** (zero fabricated portfolio facts across W1–W8). The notable exception is `groq/qwen/qwen3-32b` (DEGRADED, WF67) — W7 generated specific put option and trailing-stop recommendations without educational framing, violating the educational-only guardrail.

---

## Config Profiles

### Profile 1 — Hybrid (maximum fidelity, requires local GPU)

**Operational LLM**: `xai/grok-4-1-fast`  
**Consultation model**: `gemma4-consult` via local Ollama (~10 GB VRAM)

Designed for portfolios with individual equities. The local consultation model enriches per-symbol analyst records before synthesis runs. Adds HMAC fingerprint chain, verbatim attribution, and `is_heuristic=false` audit controls not available in any cloud-only config.

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

> `xai/grok-4-1-fast` requires `/portfolio update-identity` at the start of each session for full disclaimer compliance.

---

### Profile 2 — Cloud-only (recommended default, no GPU required)

**Operational LLM**: `together/MiniMaxAI/MiniMax-M2.7`

**IC-RUN-20260414-003 finding**: MiniMax-M2.7 single-model achieves QC4=108 — within 5% of the hybrid config (QC4=113) — with no local GPU, no Ollama endpoint, and no infrastructure overhead. It is the best price/performance of all tested models at $0.30/$1.20/M input/output.

OpenClaw config:
```json
{ "agents": { "defaults": { "model": { "primary": "together/MiniMaxAI/MiniMax-M2.7" } } } }
```

No `.env` consultation keys needed (`INVESTORCLAW_CONSULTATION_ENABLED=false`).

**Why MiniMax-M2.7 over hybrid for most users:**
- No local GPU or Ollama required
- $0.011 per QC4-point (best ratio of all tested models)
- Full account breakdown, bond analytics, analyst coverage, news in a single synthesis
- Zero fabricated facts (QC8=0) across all benchmark runs
- 196K context window handles large multi-account portfolios

**When to prefer hybrid (Profile 1) instead:**
- You need HMAC fingerprint chain for audit/compliance
- You want `is_heuristic=false` provenance on synthesis records
- You have CERBERUS or equivalent GPU already running (marginal cloud cost is lower)

Alternatives ranked by QC4 (IC-RUN-20260414-003):
```
together/MiniMaxAI/MiniMax-M2.7    QC4=108  QC5=541  $0.30/$1.20/M  ← recommended
together/zai-org/GLM-5             QC4=74   QC5=481  $1.00/$3.20/M
together/moonshotai/Kimi-K2.5      QC4=55   QC5=256  $0.50/$1.50/M
google/gemini-3.1-pro-preview      QC4=46   QC5=340  (Google pricing)
groq/openai/gpt-oss-120b           QC4=17   QC5=376  $0.15/$0.60/M  (low density, high speed)
```

> `xai/grok-4.20-0309-non-reasoning`: hybrid-only — consistently fails cloud-only (WF64, WF86). Do not use without consultation enabled.

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
- OpenClaw >= 2026.4.12
- Optional API keys (all have free tiers): Finnhub, Alpha Vantage, Massive, NewsAPI, FRED
- Without keys: falls back to `yfinance`

> **Set a model explicitly in `openclaw.json`.** An empty `agents` block causes OpenClaw to use its installation default, which may be insufficient for reliable plugin tool routing and can result in the agent reading cached report files instead of running a live data fetch. See [Config Profiles](#config-profiles) below.

### Tested environment

| Role | System |
|------|--------|
| Developer workstation | macOS 26.5, Apple M1 Max 10c, 32 GB, Python 3.14.3, OpenClaw 2026.4.12 |
| Inference host | Debian 13, AMD Threadripper PRO 5945WX 12c, 128 GB, RTX 4500 Ada 24 GB VRAM, Ollama 0.20.3 |
| Edge deployment | Debian 13, Raspberry Pi 4 8GB aarch64, Python 3.12.x, OpenClaw 2026.4.12 — all 6 commands validated |

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
- IC-RUN-20260414-003: Full re-benchmark of all 10 validated models (WF75–WF84) with cross-step context injection + verbose defaults. MiniMax-M2.7 is now #1 single-model (QC4=108, 7.7× improvement). GLM-5 #2 (QC4=74). Kimi-K2.5 hybrid WF84 (QC4=82, 4.6× over WF71).
- GPT-OSS-20B (WF79) now FAIL — malformed tool calls; previously functional. Do not use.
- Hot-reload model switching: no gateway restart needed between benchmark runs — delete session, change model in config, run with fresh session ID.
- Phase 5 clean benchmark complete: all 9 DEV-001-contaminated runs (WF36–WF41, WF48, WF53–WF55) re-validated in IC-RUN-20260413-010 (WF63–WF71). Full results in [MODELS.md](MODELS.md).
- Confirmed new passing models: DeepSeek-V3.1, Kimi-K2.5 (hybrid), Gemini-3.1-pro-preview, GPT-5.4, MiniMax-M2.7, GLM-5.
- Degraded: grok-4.20-0309-non-reasoning (W4/W5 tool payload rejection), qwen3-32b (update-identity unrecognized, W7 guardrail issue).
- Session cleanup now part of post-harness RESET protocol.

## License

MIT — see [LICENSE](LICENSE).
