# InvestorClaw

Portfolio analysis skill for OpenClaw agents. **v1.0.0** | FINOS CDM 5.x | MIT License

Provides holdings snapshots, performance metrics, bond analytics, analyst ratings, portfolio news, and CSV/Excel exports, with built-in financial advice guardrails that enforce educational-only output.

> **Naming note**: the package id is `investorclaw` (used by ClawHub and `openclaw.plugin.json`). The OpenClaw invocation command is `/portfolio`. Both names are intentional.

---

## Requirements

- Python 3.9+
- OpenClaw >= 2026.0.0
- API keys (all optional, all have free tiers):
  - [Finnhub](https://finnhub.io/register) for real-time quotes and analyst ratings
  - [NewsAPI](https://newsapi.org/register) for portfolio news correlation
  - [Polygon.io](https://polygon.io/dashboard/signup) for supplemental market data
  - [Alpha Vantage](https://www.alphavantage.co/support/#api-key) for supplemental price data
  - [FRED](https://fred.stlouisfed.org/docs/api/api_key.html) for Treasury benchmark yields

## Installation

**Via OpenClaw** (recommended): install from ClawHub or add directly from GitHub.

**Manual install**:
```bash
git clone https://github.com/perlowja/InvestorClaw.git
cd InvestorClaw
pip install -r requirements.txt
python3 tests_smoke.py
python3 investorclaw.py setup
```

For a full contributor install:
```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

Configure API keys in `.env` (copy from `.env.example`). Guided setup and first-run helpers live under `setup/` and are invoked through the entry point.

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
| `services/` | Consultation policy, portfolio consolidation, PDF extraction, utilities |
| `setup/` | First-run, installer, setup wizard, identity updater |
| `internal/` | Tier-3 enrichment internals |
| `data/` | Guardrails and symbol/reference data |
| `tests/` | Unit and contract tests |
| `pipeline.py` | Full pipeline entry for multi-step analysis |

**Not committed:**
- `.env` containing your secrets
- `portfolios/*.csv` with personal holdings
- generated files under `$INVESTOR_CLAW_REPORTS_DIR`

## Quick Start

```bash
# First-time setup
python3 investorclaw.py setup

# Holdings snapshot with live prices
python3 investorclaw.py holdings

# Performance analysis
python3 investorclaw.py performance

# Bond analytics
python3 investorclaw.py bonds

# Show all commands
python3 investorclaw.py help
```

Always invoke through `investorclaw.py`. The entry point loads `.env`, bootstraps configuration, primes model guardrails when needed, synthesizes default arguments, and routes to the correct command module.

## Commands

| Command | Aliases | Primary artifact |
|---------|---------|------------------|
| `holdings` | `snapshot`, `prices` | `holdings.json` |
| `performance` | `analyze`, `returns` | `performance.json` |
| `bonds` | `bond-analysis`, `analyze-bonds` | `bond_analysis.json` |
| `analyst` | `analysts`, `ratings` | `analyst_data.json` |
| `news` | `sentiment` | `portfolio_news.json` |
| `analysis` | `portfolio-analysis` | `portfolio_analysis.json` |
| `synthesize` | `multi-factor`, `recommend`, `recommendations` | `portfolio_analysis.json` |
| `fixed-income` | `fixed-income-analysis`, `bond-strategy` | `fixed_income_analysis.json` |
| `report` | `export`, `csv`, `excel` | `portfolio_report.{csv,xlsx}` |
| `session` | `session-init`, `risk-profile`, `calibrate` | `session_profile.json` |
| `lookup` | `query`, `detail` | targeted stdout lookup |
| `guardrails` | `guardrail`, `guardrails-prime`, `guardrails-status` | stdout |
| `ollama-setup` | `model-setup`, `consult-setup` | stdout |
| `run` | `pipeline` | pipeline stdout + artifacts |
| `setup` | `auto-setup`, `init`, `initialize` | setup output |

Output files are written to `$INVESTOR_CLAW_REPORTS_DIR` (default: `~/portfolio_reports/`).

## Output Model

InvestorClaw follows a dual-output pattern:

| Output | What it contains | Audience |
|--------|------------------|----------|
| `stdout` | Compact, token-aware JSON or human-readable command output | OpenClaw agent context |
| Disk artifact | Full JSON, CSV, or Excel output | Human review and downstream tools |

In practice, the core artifact names currently include `holdings.json`, `performance.json`, `bond_analysis.json`, `analyst_data.json`, `portfolio_news.json`, `portfolio_analysis.json`, `fixed_income_analysis.json`, and `session_profile.json`.

## Choosing Your Operational LLM

InvestorClaw uses a single-model architecture: one LLM handles routing, analysis, and guardrail enforcement via OpenClaw.

### Recommended: xAI Grok 4.1 Fast

Model ID: `xai/grok-4-1-fast`

- 2M token context window, handles large portfolios and long sessions without truncation
- Fast reasoning mode with strong financial analysis quality
- Sign up at [console.x.ai](https://console.x.ai)
- Cost: ~$10–20/month for typical portfolio analysis workloads

### Alternative: OpenAI GPT-4.1-nano

Model ID: `openai/gpt-4.1-nano`

- 1M token context window, sufficient for most individual portfolios
- Tier 1 rate limit is **30K TPM shared across all session activity**
- Sign up at [platform.openai.com](https://platform.openai.com)
- Cost: ~$10–20/month for typical workloads

### On-Premise: NemoClaw (NVIDIA NIM)

For organizations that cannot send portfolio data to external APIs, NemoClaw distributes NVIDIA Nemotron models via the OpenClaw NVIDIA NIM integration. See the [NemoClaw documentation](https://github.com/NVIDIA/NemoClaw) for deployment details.

## Local Consultation Model (Optional)

InvestorClaw supports a two-layer architecture:

1. **Operational LLM** for routing, conversation, and guardrail handling via OpenClaw
2. **Consultation model** (local Ollama) for structured portfolio synthesis before the operational model sees the result

Enable via `.env`:
```bash
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

`gemma4-consult` is the default recommended model. The consultation policy lives in `services/consultation_policy.py`. Today, tier-3 consultation is injected for analyst commands when enabled.

## Portfolio File Format

Place CSV or Excel (`.xls`, `.xlsx`) files in `portfolios/` or set `$INVESTOR_CLAW_PORTFOLIO_DIR`.

Run `python3 investorclaw.py setup` for guided column mapping and portfolio discovery if your broker uses non-standard column names.

## Security

InvestorClaw includes several safety measures:

- PII scrubbing for sensitive identifiers found in imported portfolio data
- Prompt-injection scanning on untrusted text fields
- Deterministic Python calculations for portfolio math
- Optional local consultation to keep raw portfolio data on-premise
- Educational-only financial guardrails via `data/guardrails.yaml`

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

## Compliance

**NOT INVESTMENT ADVICE.** InvestorClaw provides educational portfolio analysis only. It is not a substitute for professional financial advice and does not assess personal risk tolerance, goals, or investment suitability.

## License

MIT, see [LICENSE](LICENSE).
