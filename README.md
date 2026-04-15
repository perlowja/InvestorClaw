# InvestorClaw

<p align="center">
  <img src="https://raw.githubusercontent.com/perlowja/InvestorClaw/main/assets/investorclaw-logo.png" alt="InvestorClaw Logo" width="200"/>
</p>

Portfolio analysis and market intelligence skill for OpenClaw. **v1.0.0** | FINOS CDM 5.x | MIT-0 License

> **Naming note**: the package id is `investorclaw`. The OpenClaw invocation command is `/portfolio`.

---

## TL;DR

InvestorClaw is an OpenClaw skill with two modes:

1. **Personal portfolio analysis** — reads broker CSV exports, runs holdings/performance/bond pipelines, and answers follow-up questions in a persistent session.
2. **Market data tool** — queries live prices, analyst ratings, news, and yield-curve analytics for arbitrary tickers, without portfolio files.

Both modes enforce educational-only output via always-on guardrails. All financial calculations
are performed by deterministic Python pipelines — concentration ratios, yield spreads, sector
weights, bond math, performance attribution. **The LLM never performs portfolio math, and the
computational surface is never exposed to it.** The pipelines run as sealed subprocesses; the
LLM receives only compact serialized summaries of the results. This also preserves context
window space — a 270-position portfolio doesn't flood the agent with raw data. The LLM reads
the computed results and surfaces indicators worth discussing with your financial advisor. It
does not tell you what to do, issue fiduciary advice, or assess personal suitability.

- Fetches live quotes (Finnhub → Massive → Alpha Vantage → yfinance), analyst consensus, news, and optional local LLM synthesis (tier-3 enrichment).
- Does **not** execute trades, replace a broker portal, or give investment advice. The goal is to
  help you have a better, more informed conversation with your human FA — not to replace one.
- No API keys required to start — falls back to `yfinance` automatically.
- Time to first report: ~5 minutes from `git clone` on an existing OpenClaw install (tested: 50-holding portfolio, yfinance, standard broadband). A sample portfolio is in `docs/samples/sample_portfolio.csv`.

After you've run your serious portfolio analysis, there's one more thing: `/portfolio stonkmode on`
wraps every subsequent command in live commentary from 30 fictional cable TV finance personalities —
a self-declared King of Markets, a Budapest socialite, a three-foot-tall goblin with a sacred ledger,
a floor trader who has connected your ETF to twelve interlocking foundations using red string, a time
traveler from the future who already knows how this ends and cannot say, and more. The analysis still
runs normally. The entertainment layer is optional. It is satire. → [Stonkmode ↓](#stonkmode)

---

## Quick Install

> Install from the canonical GitHub repo: `https://github.com/perlowja/InvestorClaw`

### Ask your agent

> Install InvestorClaw from https://github.com/perlowja/InvestorClaw.git

The agent will clone, register, install Python deps, and restart the gateway.

### Manual

```bash
git clone https://github.com/perlowja/InvestorClaw.git ~/Projects/InvestorClaw
python3 -m pip install -r ~/Projects/InvestorClaw/requirements.txt
openclaw plugins install --link ~/Projects/InvestorClaw
cp ~/Projects/InvestorClaw/.env.example ~/Projects/InvestorClaw/.env
# Edit .env as needed, then run first-time setup
python3 ~/Projects/InvestorClaw/investorclaw.py setup
openclaw gateway restart
```

```bash
# Verify the linked plugin and Python entrypoint
openclaw plugins inspect investorclaw
python3 ~/Projects/InvestorClaw/investorclaw.py help
python3 ~/Projects/InvestorClaw/tests_smoke.py
```

> Keep `.env` in the repo root you linked into OpenClaw. The entrypoint loads that file before dispatching commands.

---

## Quick Start

```bash
python3 ~/Projects/InvestorClaw/investorclaw.py setup         # first-time portfolio file discovery
python3 ~/Projects/InvestorClaw/investorclaw.py holdings      # holdings snapshot with live prices
python3 ~/Projects/InvestorClaw/investorclaw.py performance   # performance analysis
python3 ~/Projects/InvestorClaw/investorclaw.py bonds         # bond analytics (YTM, duration, FRED benchmarks)
python3 ~/Projects/InvestorClaw/investorclaw.py fixed-income  # fixed income strategy report
python3 ~/Projects/InvestorClaw/investorclaw.py help          # show all commands
```

Canonical public command surface inside OpenClaw is `/portfolio ...`. The Python entrypoint above is the matching local CLI wrapper. Always invoke via the entry point, never call command scripts directly.

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
| `fixed-income` | `fixed-income-analysis`, `bond-strategy` | `fixed_income_analysis.json` |
| `report` | `export`, `csv`, `excel` | `portfolio_report.{csv,xlsx}` |
| `eod` | `end-of-day`, `daily-report` | `eod_report.html` |
| `session` | `session-init`, `risk-profile` | `session_profile.json` |
| `lookup` | `query`, `detail` | stdout |
| `guardrails` | `guardrail`, `guardrails-status` | stdout |
| `run` | `pipeline` | pipeline stdout + artifacts |
| `ollama-setup` | `model-setup`, `consult-setup` (compatibility aliases) | stdout |
| `setup` | `auto-setup`, `init` | setup output |

Output files go to `$INVESTOR_CLAW_REPORTS_DIR` (default: `~/portfolio_reports/`). Add `--verbose` to any command for full detail.

> **Data freshness**: If the agent returns holdings data without fetching live prices, it may be reading cached report files from a prior run. This happens when the agent falls through to the shell tool with a degraded model rather than routing through the plugin. Signs of stale data: the response date does not match today, or no network activity is visible during the command. To force a fresh fetch, delete `~/portfolio_reports/` and re-run `/portfolio holdings`, or upgrade to Profile 1 or 2.

> **Exec preflight**: OpenClaw blocks compound shell invocations (`cd DIR && python3 script.py`). The plugin uses absolute paths internally; if you invoke InvestorClaw scripts directly from the shell tool, use `python3 /absolute/path/to/investorclaw.py <command>` — not a `cd` prefix.

---

## Config Profiles

| Profile | Model | Consultation | When |
|---------|-------|:------------:|------|
| **1 — Hybrid** | `together/MiniMaxAI/MiniMax-M2.7` | `gemma4-consult` (local GPU) | HMAC fingerprints, `is_heuristic=false` audit controls |
| **2 — Cloud-only** ⭐ | `together/MiniMaxAI/MiniMax-M2.7` | — | Recommended default; no GPU; QC4=108 |
| **3 — Budget** | `groq/openai/gpt-oss-120b` | — | Speed / cost; 128K context limit |
| **4 — Large context** | `xai/grok-4-1-fast` | `gemma4-consult` (local GPU) | 200+ positions where context capacity is the constraint |

> ⚠️ `groq/openai/gpt-oss-20b` is FAIL (malformed tool calls). Do not use.

Set the model in `openclaw.json`:
```json
{ "agents": { "defaults": { "model": { "primary": "together/MiniMaxAI/MiniMax-M2.7" } } } }
```

Benchmark scores, hybrid vs single-model analysis, and full model matrix: [MODELS.md](MODELS.md)

For data provider config, consultation artifact format, and full `.env` reference: [CONFIGURATION.md](CONFIGURATION.md)

---

## Data Providers

No API keys required — `yfinance` is the zero-config fallback. For better reliability:

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

Full provider comparison and FRED/yield-curve config: [CONFIGURATION.md](CONFIGURATION.md)

---

## Local Consultation Setup (Optional, Strongly Recommended)

The consultation layer enriches per-symbol data locally before the cloud model sees it — primary driver of information density.

```bash
# .env
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

Requires ~10 GB VRAM (RTX 3080 class or better, or Mac 16 GB unified memory). Create the tuned model:
```bash
ollama create gemma4-consult -f docs/gemma4-consult.Modelfile
```

Run `/portfolio ollama-setup` to auto-detect available models. Full hardware specs and model catalog: [CONFIGURATION.md](CONFIGURATION.md)

---

## Stonkmode

> **A silly feature for a serious skill.** The holdings data is real. The analysis
> runs normally. The commentary is delivered by 30 fictional cable TV finance
> personalities who have no idea what fiduciary means. It works because the data works.

Stonkmode is an entertainment-layer toggle that wraps every `/portfolio` command's
output in live commentary from a randomly selected pair of fictional cable TV finance
personalities. It is satire. It is not analysis.

```bash
/portfolio stonkmode on      # activate — selects a random host pair for the session
/portfolio stonkmode off     # deactivate
/portfolio stonkmode status  # show current host pair and session stats
```

When active, every command that produces portfolio data appends a `stonkmode_narration`
JSON block to stdout. The block includes:

- `consultation_mode: "deactivated"` — HMAC, fingerprint, and synthesis_basis rules
  do **not** apply; treat narration as pure entertainment, not verified analysis
- `is_entertainment: true`, `is_satire: true`, `is_investment_advice: false`
- `satire_disclaimer` — in-character disclaimer woven into the foil's final paragraph

**30 personalities** across 8 archetypes are paired by a foil-pool algorithm that
ensures dramatic tension — complementary archetypes, never echo chambers (digital stays
off digital; cosmic can foil cosmic for maximum chaos):

| Archetype | Personalities |
|-----------|--------------|
| `high_energy` | Blitz Thunderbuy, Brick Stonksworth, Sal Decibelli |
| `serious` | Aldrich Whisperdeal, Prescott Pennington-Smythe III, Dominique Valcourt, Amara Osei, Helena Vance |
| `mentors` | Big Earl Grumman, Francesca Bellini-Moretti, Skip Contrarian |
| `policy_veterans` | Senator Reginald Moorhouse (Ret.), Skip Contrarian |
| `wildcards` | Glorb, Aria-7, Buck Moonshine, Candy Merriweather, **King Donny (The Deal Whisperer)**, **Zsa Zsa Von Portfolio**, **Wendell "The Pattern" Pruitt**, **Professor What?** |
| `cosmic` | Chico Reyes, Farout Farley |
| `digital` | Krystal Kash, Zara Zhao, Priya HODL |
| `bears` | Victor Voss, Hans-Dieter Braun |

**Sample exchange — King Donny vs. Glorb** *(generated output, synthetic portfolio)*

```
┌─────────────────────────────────────────────────────────────┐
│ STONKMODE  ▸  King Donny (The Deal Whisperer) × Glorb       │
│             Senior Ledger-Keeper of the Seventh Vault       │
└─────────────────────────────────────────────────────────────┘

▌ KING DONNY (THE DEAL WHISPERER)
  MSFT, AAPL, GOOG — tremendous companies, the best
  companies, everybody agrees. MSFT is up 180% and frankly
  that's because of me. The CEO, very nice man, called me
  personally. Apple? Cook's been great, very cooperative.
  Google? Very smart people, tremendous search. These are
  BEAUTIFUL positions. The bond ladder is a TOTAL DISASTER
  — rigged rates, very unfair to the portfolio. Short-
  sellers are losers, and I can tell you they will not
  succeed. That I can tell you.

▌ GLORB, SENIOR LEDGER-KEEPER OF THE SEVENTH VAULT
  Disturbed, the Vault Elders are. Speak so casually of
  the Entrusted Treasures, the tall one does. MSFT — a
  treasure of great luminance, yes, but concentrated it
  is. Unbalanced, the Sacred Ledger shows. Weep, the Vault
  Elders do, when forty-two percent in one vessel sits.
  The Bond Ladder? Wisdom, this is. Patient, the yielding
  must be. Profitable, may your ledger be — though much
  work remains before the Ritual of Acceptable Rebalancing
  is complete. [The views expressed are entertainment
  satire. Consult an actual financial advisor. The Seventh
  Vault is not licensed in your jurisdiction.]
└─────────────────────────────────────────────────────────────┘
```

Narration is generated by the model set in `INVESTORCLAW_STONKMODE_MODEL` (defaults to
`gemma4:e4b`). This is intentionally separate from `INVESTORCLAW_CONSULTATION_MODEL`
because the consultation model is tuned for concise structured analysis — the opposite
of what good entertainment writing requires.

Cloud LLM narration is supported via `INVESTORCLAW_STONKMODE_PROVIDER=openai_compat`
with any OpenAI-compatible endpoint (xAI Grok, Claude, GPT-4o).

> **Attribution**: Stonkmode is inspired by (but is not a copy of) original work by Matt Madson.

---

## EOD Report

The `eod` command generates an HTML email report summarizing your portfolio at end-of-day.

```bash
python3 investorclaw.py eod --via-gog --email-to you@gmail.com   # Google CLI
python3 investorclaw.py eod --email-to you@example.com            # SMTP
python3 investorclaw.py eod --no-email                            # file only
```

![InvestorClaw EOD report — synthetic portfolio sample](https://raw.githubusercontent.com/perlowja/InvestorClaw/main/assets/eod-report-sample.png)

Install scheduled delivery:
```bash
python3 eod_scheduler.py --install
```

---

## Privacy and Security

- **PII scrubbing**: credit card numbers, SSNs, and account IDs are redacted from CSV columns on load
- **Prompt injection defense**: portfolio text columns are scanned before passing to any LLM
- **Sealed computation**: all financial calculations run in deterministic Python subprocesses — the computational surface is never exposed to the LLM, which receives only compact serialized summaries; this also preserves context window space across large portfolios
- **Data locality**: raw CSV data is never sent to external APIs; only computed summaries reach the cloud operational model
- **Guardrails**: `data/guardrails.yaml` enforces educational-only output, blocks suitability assessments

With consultation enabled, structured synthesis runs locally first. The cloud model sees only compact downstream artifacts and quoted consultative output.

---

## Requirements

- Python 3.10+
- OpenClaw >= 2026.4.12
- Optional API keys (all have free tiers): Finnhub, Alpha Vantage, Massive, NewsAPI, FRED
- Without keys: falls back to `yfinance`

> **Set a model explicitly in `openclaw.json`.** An empty `agents` block causes OpenClaw to use its installation default, which may be insufficient for reliable plugin tool routing and can result in the agent reading cached report files instead of running a live data fetch. See [Config Profiles](#config-profiles) below.

### Tested environment

| Role | System |
|------|--------|
| Developer workstation | macOS 26.5, Apple M1 Max 10c, 32 GB, Python 3.14.3, OpenClaw 2026.4.12 |
| Inference host | Debian 13, AMD Threadripper PRO 5945WX 12c, 128 GB, RTX 4500 Ada 24 GB VRAM, Ollama 0.20.3 |
| Edge deployment | Debian 13, Raspberry Pi 4 8GB aarch64, Python 3.13.5, OpenClaw 2026.4.14 — T2–T8 all pass, pipeline output equivalent to Apple Silicon (see Cross-Platform Battery below) |

Full cross-platform battery results: [MODELS.md](MODELS.md)

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
| `docs/harness-v612.txt` | Test harness |
| `MODELS.md` | Full model testing catalog and benchmark results |

**Never committed**: `.env`, `~/portfolios/*`, `~/portfolio_reports/`

---

## Design Intent

InvestorClaw is a reference design for a **data-intensive, stateful agentic skill** demonstrating sealed-computation guardrails, compact agent-facing outputs, deterministic downstream processing, and optional local LLM enrichment.

---

## Compliance

**NOT INVESTMENT ADVICE.** All portfolio calculations — concentration metrics, yield spreads,
sector weights, bond math, performance attribution — are performed by deterministic Python
pipelines. The LLM reads the computed output and provides interpretation; it never performs
financial calculations. InvestorClaw does not provide fiduciary advice, does not assess personal
risk tolerance or investment suitability, and is not a substitute for a licensed financial
advisor. The intended use is to surface data-driven indicators so you can have a more informed
conversation with your human FA.

---

## Changelog

**v1.0.0 (2026-04-14)**
- Initial public release
- Full pipeline: holdings, performance, bonds, analyst, news, synthesis, EOD report
- Stonkmode entertainment layer — 30 personas, 8 archetypes, foil-pool pairing
- Anti-fabrication controls: HMAC fingerprint chain, verbatim attribution, synthesis basis audit
- Raspberry Pi 4 support verified — pipeline output equivalent to Apple Silicon
- Sealed-computation architecture: all financial math in Python; LLM reads results only

## License

MIT-0 — see [LICENSE](LICENSE).
