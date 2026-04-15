# InvestorClaw — Configuration Reference

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

Run `/portfolio ollama-setup` to auto-detect available models on your endpoint. `consult-setup` remains as a compatibility alias, not the primary public command.

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
