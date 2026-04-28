# InvestorClaw — Configuration Reference

**Version**: 2.1.9 | **Updated**: 2026-04-23

---

## Configuration Precedence (Priority Order)

InvestorClaw applies configuration in this order (highest → lowest):

1. **Shell/Agent Overrides** — `export INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat` (never overwritten)
2. **Setup Wizard Config** (`~/.investorclaw/setup_config.json`) — applied via `os.environ.setdefault()`
3. **Skill-Level Defaults** (`skill/.env`) — applied last via `os.environ.setdefault()`

**Key principle**: Always use `os.environ.setdefault()`, never direct assignment. This ensures shell overrides are always respected.

---

## Data Providers

| Provider | Quotes | History | News | Analyst | Free tier |
|----------|:------:|:-------:|:----:|:-------:|-----------|
| **yfinance** | ✅ | ✅ | ✅ | ✅ | Unlimited — no key |
| **Finnhub** | ✅ fast | ❌ 403 free | ✅ | ⚠️ unreliable free | 60 req/min |
| **Massive** | ✅ batch 268ms | ✅ full OHLCV | ✅ | ❌ | Prev-day only (paid recommended) |
| **Alpha Vantage** | ✅ sequential | ✅ adjusted EOD | ❌ | ✅ earnings proxy | 25 req/day |
| **NewsAPI** | ❌ | ❌ | ✅ | ❌ | 100 req/day |

```bash
# Zero-cost
INVESTORCLAW_PRICE_PROVIDER=yfinance

# Free with keys
INVESTORCLAW_PRICE_PROVIDER=auto
INVESTORCLAW_FALLBACK_CHAIN=finnhub,alpha_vantage,yfinance
FINNHUB_KEY=...   ALPHA_VANTAGE_KEY=...   NEWSAPI_KEY=...

# Recommended for regular use
INVESTORCLAW_PRICE_PROVIDER=massive
MASSIVE_API_KEY=...   FINNHUB_KEY=...
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

## Local Consultation Models

The consultation layer enriches per-symbol analyst data locally before the cloud operational model sees the result. This is the primary driver of information density — not model capability.

**Hardware**: ~10 GB VRAM (RTX 3080 class or better, CUDA 8.0+, or Mac 16 GB unified memory). Ollama >= 0.20.x.

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

Run `/investorclaw:investorclaw-llm-config` to auto-detect available models on your endpoint. `consult-setup` remains as a compatibility alias, not the primary public command.

| Model | tok/s | VRAM | Notes |
|-------|-------|------|-------|
| `gemma4-consult` | ~65 | ~10 GB | Recommended — tuned Modelfile for concise structured analysis |
| `gemma4:e4b` | ~66 | ~10 GB | Base model; use if Modelfile not available |
| `gemma4:e2b` | ~99 | ~7 GB | Faster; lighter analysis density |
| `qwen2.5:14b-instruct-q4_K_M` | ~45 | ~9 GB | Alternative for structured output |

---

## Environment Variables

All keys are optional — yfinance is the zero-config fallback. See `.env.example` for the full annotated list.

| Variable | Purpose | Default |
|----------|---------|---------|
| `INVESTOR_CLAW_PORTFOLIO_DIR` | Directory containing broker CSV exports | skill `portfolios/` |
| `INVESTOR_CLAW_REPORTS_DIR` | Output directory for JSON/CSV/HTML reports | `~/portfolio_reports/` |
| `INVESTORCLAW_PRICE_PROVIDER` | Primary price provider (`massive`, `finnhub`, `yfinance`, `auto`) | `yfinance` |
| `INVESTORCLAW_FALLBACK_CHAIN` | Ordered fallback list | `massive,finnhub,yfinance` |
| `INVESTORCLAW_CONSULTATION_ENABLED` | Enable local enrichment layer | `false` |
| `INVESTORCLAW_CONSULTATION_ENDPOINT` | Ollama endpoint URL | — |
| `INVESTORCLAW_CONSULTATION_MODEL` | Consultation model ID | `gemma4-consult` |
| `INVESTORCLAW_CONSULTATION_HMAC_KEY` | HMAC signing key for fingerprint chain | — |
| `INVESTORCLAW_STONKMODE_MODEL` | Model for stonkmode narration | `gemma4:e4b` |
| `INVESTORCLAW_STONKMODE_PROVIDER` | `ollama` or `openai_compat` | `ollama` |
| `FINNHUB_KEY` | Finnhub API key | — |
| `MASSIVE_API_KEY` | Polygon/Massive API key | — |
| `ALPHA_VANTAGE_KEY` | Alpha Vantage key | — |
| `NEWSAPI_KEY` | NewsAPI key | — |
| `FRED_API_KEY` | FRED (St. Louis Fed) key for Treasury/TIPS benchmarks | — |

---

## Narrative Configuration (v1.0.1+)

New in v1.0.1: Unified `INVESTORCLAW_NARRATIVE_*` variables replace legacy `INVESTORCLAW_STONKMODE_*` (still supported for backward compat).

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `INVESTORCLAW_NARRATIVE_PROVIDER` | string | `ollama` | Provider: `ollama` (local) or `openai_compat` (cloud) |
| `INVESTORCLAW_NARRATIVE_ENDPOINT` | string | — | Base URL for narration provider |
| `INVESTORCLAW_NARRATIVE_API_KEY` | string | — | Bearer token for cloud providers (not needed for local Ollama) |
| `INVESTORCLAW_NARRATIVE_MODEL` | string | `gemma4:e4b` | Model name for stonkmode narration |
| `INVESTORCLAW_STONKMODE_DISABLED` | bool | — | Set to `true` to disable stonkmode in CI/test environments |

**Examples:**

```bash
# Together.ai (recommended for cost-sensitive deployments)
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=<together_key>
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7

# xAI Grok (high-context, when Together.ai unavailable)
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.x.ai/v1
INVESTORCLAW_NARRATIVE_API_KEY=<xai_key>
INVESTORCLAW_NARRATIVE_MODEL=grok-4-1-fast

# Local Ollama (air-gapped, no cloud APIs)
INVESTORCLAW_NARRATIVE_PROVIDER=ollama
INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:11434
INVESTORCLAW_NARRATIVE_MODEL=gemma4:e4b
```

---

## Deployment Modes

| Mode | Use Case | Output Format | Guardrails |
|------|----------|---|---|
| `single_investor` (default) | Individual/retail portfolios | Detailed, narrative-heavy | Educational only, no advice |
| `fa_professional` | FA/advisor deployments | Structured, data-focused | Professional framing allowed |

```bash
INVESTORCLAW_DEPLOYMENT_MODE=single_investor  # Default
```

---

## Scenario-Based Configuration

### Scenario A: Cloud-Only (Recommended — 99% of users)

**Setup**: No GPU required. All inference via cloud APIs.

```bash
# .env
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=<together_key>
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7

FINNHUB_KEY=<optional>
NEWSAPI_KEY=<optional>
```

**No consultation needed.** Stonkmode narration via Together.ai/xAI. Price data from yfinance (free).

### Scenario B: Hybrid (Cloud narrative + Local consultation)

**Setup**: GPU host (10–12 GB VRAM) running llama-server on port 8080.

```bash
# .env
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=<together_key>
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7

INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://192.0.2.96:8080
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

**Start GPU service**: `ssh gpu-host "systemctl start llama-gemma4"`

### Scenario C: Air-Gapped (Local-Only)

**Setup**: All inference local. Zero cloud APIs.

```bash
# .env (all local, no cloud keys)
INVESTORCLAW_NARRATIVE_PROVIDER=ollama
INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:11434
INVESTORCLAW_NARRATIVE_MODEL=gemma4:e4b

INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult

INVESTORCLAW_PRICE_PROVIDER=yfinance  # Only free provider; no key needed
```

**Start services**: `ollama serve` (narration) + `systemctl start llama-gemma4` (consultation)

---

## Troubleshooting Configuration

**Issue**: Narration never emits (stonkmode silent)
- **Check 1**: Is `INVESTORCLAW_NARRATIVE_PROVIDER` set?
- **Check 2**: Run `/portfolio stonkmode on` to activate state file
- **Check 3**: Is endpoint reachable? `curl http://<endpoint>/v1/models` (or `/api/tags` for Ollama)
- **Fix**: Verify env vars and endpoint, then retry

**Issue**: "Missing API key" for data provider
- **Fix**: Set in `.env` or export: `export FINNHUB_KEY=pk_...`
- **Fallback**: All features degrade gracefully without optional keys

**Issue**: Consultation endpoint unreachable but narration works
- **Fix**: Disable consultation (`INVESTORCLAW_CONSULTATION_ENABLED=false`) or ensure GPU host is running

**Issue**: API rate limits hit during news fetching
- **Fix**: Set `INVESTORCLAW_SKIP_NEWS=true` to skip news (faster)
- **Fix**: Increase timeout: `INVESTORCLAW_API_TIMEOUT=30`

---

## Configuration Validation

Before production, verify:

```bash
# Check all required env vars are set
investorclaw setup

# Test price provider
investorclaw lookup --symbol AAPL

# Test analyst consensus (requires FINNHUB_KEY)
investorclaw analyst

# Test narration endpoint
curl -v http://<INVESTORCLAW_NARRATIVE_ENDPOINT>/v1/models
# or for Ollama:
curl -v http://<INVESTORCLAW_NARRATIVE_ENDPOINT>/api/tags

# Test full pipeline
investorclaw holdings
# Should output stonkmode_narration JSON block if stonkmode enabled
```
