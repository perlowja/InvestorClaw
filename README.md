# InvestorClaw

<p align="center">
  <img src="https://raw.githubusercontent.com/perlowja/InvestorClaw/main/assets/investorclaw-logo.png" alt="InvestorClaw Logo" width="200"/>
</p>

Portfolio analysis and market intelligence skill for OpenClaw and other agentic systems. **v1.0.0** | FINOS CDM 5.x | MIT License

> **Naming note**: the package id is `investorclaw` (used by the ClawHub marketplace and `openclaw.plugin.json`). The OpenClaw invocation command is `/portfolio` — that is what users type at the prompt. Both names are intentional.

---

## TL;DR

InvestorClaw is an OpenClaw skill with two distinct use cases:

1. **Personal portfolio analysis** — reads your broker CSV exports, runs holdings/performance/bond pipelines, and answers follow-up questions in a persistent session.
2. **General market data & news tool** — any agentic system (OpenClaw, Claude, custom agents) can query live prices, analyst ratings, news correlation, and yield-curve analytics for arbitrary tickers, without any portfolio files required.

Both modes share the same guardrails that enforce educational-only output.

- **What it does**: fetches live quotes (Finnhub → Massive → Alpha Vantage → yfinance), analyst consensus, news summaries, fixed-income analytics, and optional LLM consultation synthesis via a local Ollama model (CERBERUS tier-3 enrichment).
- **What it does not do**: execute trades, replace your broker portal, or give investment advice.
- **Time to first report**: roughly 5 minutes from `git clone` to `holdings.json` on an existing OpenClaw install.
- **No API keys required to start**: falls back to `yfinance` automatically; add keys later for better reliability.
- **Guardrails are always on**: every output is bounded to educational analysis — the skill cannot be prompted into suitability assessments or specific buy/sell calls.

---

## Quick Install

> **ClawHub marketplace listing is in progress.** Until then, install from GitHub.

### Ask your agent (easiest)

**Say this to your OpenClaw or Claude agent:**

> Install InvestorClaw from https://github.com/perlowja/InvestorClaw.git

The agent will clone the repo, register the plugin with `openclaw plugins install --link`, install Python dependencies, and restart the gateway.

### Manual steps

```bash
git clone https://github.com/perlowja/InvestorClaw.git ~/Projects/InvestorClaw
pip install -r ~/Projects/InvestorClaw/requirements.txt
openclaw plugins install --link ~/Projects/InvestorClaw
cp ~/Projects/InvestorClaw/.env.example ~/Projects/InvestorClaw/.env
# Edit .env — add at minimum FINNHUB_KEY for market data
python3 ~/Projects/InvestorClaw/investorclaw.py setup
openclaw gateway restart
```

Verify the plugin loaded:
```bash
openclaw plugins inspect investorclaw
python3 ~/Projects/InvestorClaw/tests_smoke.py
```

### Developer / contributor install

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

API key configuration is managed through `.env` (copied from `.env.example`) and optionally through the OpenClaw plugin config schema (`INVESTOR_CLAW_REPORTS_DIR`, `INVESTOR_CLAW_PORTFOLIO_DIR`, and provider key overrides).

---

## Quick Start

```bash
# First-time setup: portfolio file discovery and column mapping
python3 investorclaw.py setup

# Holdings snapshot with live prices
python3 investorclaw.py holdings

# Performance analysis
python3 investorclaw.py performance

# Bond analytics (YTM, duration, FRED benchmarks)
python3 investorclaw.py bonds

# Show all commands
python3 investorclaw.py help
```

Always invoke via the entry point — never call command scripts directly. The entry point loads `.env`, bootstraps configuration, primes guardrails when needed, synthesizes default arguments, and routes to the correct command module.

---

## Daily Portfolio Report (`eod`)

The `eod` command generates a fully self-contained HTML email report summarizing your portfolio at end-of-day and delivers it via your configured mail transport.

### Basic usage

```bash
# Deliver via gog (Google CLI — recommended)
python3 investorclaw.py eod --via-gog --email-to you@gmail.com

# Deliver via SMTP
python3 investorclaw.py eod --email-to you@example.com

# Generate the file only, no email
python3 investorclaw.py eod --no-email

# Run the full analysis pipeline first, then generate and send the report
python3 investorclaw.py eod --run --via-gog --email-to you@gmail.com
```

### What the report contains

- **Portfolio summary**: total value, daily P&L, top movers
- **Account breakdown**: holdings grouped by account type (401K, IRA, Roth IRA, SEP-IRA, brokerage)
- **Sector allocation**: pie-style breakdown with ETF / Diversified detection
- **Bond positions**: duration, YTM, FRED benchmark spread (when bond data is available)
- **News tailwinds and risks**: top positive and negative news items rendered as clickable `[SYMBOL]` links resolved from `top_positive` / `top_negative` in the news artifact
- **Macro themes**: rule-based extraction from news keywords covering five themes — AI & Technology, Trade Policy, Interest Rates, Corporate Earnings, and Energy — with no LLM call required

### Visual design

The report uses a dark/high-contrast theme (GitHub Dark-inspired palette) that passes WCAG AA contrast ratios. Layout is two-column for desktop and stacks to a single column on screens 600px and narrower via CSS media queries, making it readable on mobile without a separate template.

### Delivery options

| Flag | Transport | Notes |
|------|-----------|-------|
| `--via-gog` | `gog` Google CLI | Recommended; uses your authenticated Google account |
| *(no flag)* | SMTP | Uses `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASS` / `SMTP_FROM` |
| `--no-email` | File only | Writes to `$INVESTOR_CLAW_REPORTS_DIR/eod_report.html` |

### Scheduled delivery

Install the scheduler to send the report automatically at market close:

```bash
python3 eod_scheduler.py --install
```

This installs a cron job (or launchd plist on macOS) that runs the full pipeline and delivers the report at the configured time. Uninstall with `python3 eod_scheduler.py --uninstall`.

### Relevant `.env` variables

| Variable | Purpose |
|----------|---------|
| `EOD_EMAIL_TO` | Default recipient address (overridden by `--email-to`) |
| `INVESTOR_CLAW_EOD_GOG` | Set to `true` to default `--via-gog` without the flag |
| `INVESTOR_CLAW_GOG_ACCOUNT` | Google account identifier for `gog` sends |
| `SMTP_HOST` | SMTP relay hostname |
| `SMTP_PORT` | SMTP port (default: 587) |
| `SMTP_USER` | SMTP auth username |
| `SMTP_PASS` | SMTP auth password |
| `SMTP_FROM` | From address for SMTP sends |

---

## Portfolio & Account Features

### ETF sector identification

ETFs and ETF-like instruments — including diversified holding companies such as BRK.B — are identified automatically and reported as "ETF / Diversified" in sector breakdowns rather than assigned a misleading single-sector label.

### Account type breakdown

Holdings are grouped by account type in reports and the `eod` output. InvestorClaw auto-detects account type from account names in your CSV data, covering the common personal account taxonomy: 401K, IRA, Roth IRA, SEP-IRA, and taxable brokerage. Use `ACCOUNT_LABELS` to map raw CSV account IDs to readable display names.

### ESPP holding detection

Employer stock plan positions are identified via the `ESPP_HOLDINGS` environment variable. When a symbol is marked as ESPP:

- it is correctly attributed to the specified account regardless of CSV row order
- it is excluded from concentration warnings (employer stock is a known, deliberate concentration)
- multiple accounts per symbol are supported using a semicolon separator

```bash
# Single account
ESPP_HOLDINGS=ACME:BrokerageAccount

# Multiple symbols and accounts
ESPP_HOLDINGS=ACME:BrokerageAccount;ACME:EmployeeStockPlan,WIDG:BrokerageAccount
```

### Managed account flagging

Accounts listed in `MANAGED_ACCOUNTS` are flagged as discretionary or advisor-managed in the analysis context. This matters for concentration analysis: positions in managed accounts reflect advisor decisions, not self-directed choices, and the report surfacing this distinction avoids misleading FA-discussion topics.

```bash
MANAGED_ACCOUNTS=AdvisorManagedIRA,ManagedBrokerage
```

### CIT / pooled fund support

Collective Investment Trust funds (for example, "Fidelity Contrafund Pool CL F" common in 401K plans) use non-conflicting ticker symbols that do not collide with public equities. When a live price provider cannot resolve the symbol, InvestorClaw uses the broker-supplied NAV from the CSV as the fallback price rather than failing the position.

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
| `synthesize` | `multi-factor`, `recommend`, `recommendations` | `portfolio_analysis.json` |
| `fixed-income` | `fixed-income-analysis`, `bond-strategy` | `fixed_income_analysis.json` |
| `report` | `export`, `csv`, `excel` | `portfolio_report.{csv,xlsx}` |
| `eod` | `end-of-day`, `daily-report` | `eod_report.html` |
| `session` | `session-init`, `risk-profile`, `calibrate` | `session_profile.json` |
| `lookup` | `query`, `detail` | targeted stdout lookup |
| `guardrails` | `guardrail`, `guardrails-prime`, `guardrails-status` | stdout |
| `update-identity` | `update_identity`, `identity` | — |
| `run` | `pipeline` | pipeline stdout + artifacts |
| `ollama-setup` | `model-setup`, `consult-setup` | stdout |
| `setup` | `auto-setup`, `init`, `initialize` | setup output |

Output files are written to `$INVESTOR_CLAW_REPORTS_DIR` (default: `~/portfolio_reports/`).

Add `--verbose` to any command for full detail (default is compact/summary output).

---

## Configuration Reference

All configuration lives in `.env` (copied from `.env.example`). The table below documents every supported variable.

### Market data providers

| Variable | Values / Notes |
|----------|---------------|
| `INVESTORCLAW_PRICE_PROVIDER` | `auto` (default), `yfinance`, `finnhub`, `massive` — primary quote provider |
| `INVESTORCLAW_FALLBACK_CHAIN` | Comma-separated ordered fallback list, e.g. `finnhub,alpha_vantage,yfinance` |
| `INVESTOR_CLAW_REFRESH_PRICES` | `true` / `false` — when `true`, re-fetches live prices even when a broker snapshot exists in the CSV; `false` uses broker-supplied NAV/price as the canonical value (useful for CIT funds and after-hours snapshots) |
| `FINNHUB_KEY` | Finnhub API key (60 req/min free) |
| `MASSIVE_API_KEY` | Massive / Polygon-compatible API key |
| `ALPHA_VANTAGE_KEY` | Alpha Vantage API key (25 req/day free) |
| `NEWSAPI_KEY` | NewsAPI key (100 req/day free) |
| `FRED_API_KEY` | FRED API key for Treasury benchmark yields |

### Portfolio and account identity

| Variable | Values / Notes |
|----------|---------------|
| `ESPP_HOLDINGS` | `SYMBOL:AccountName` pairs, comma-separated; use semicolons between multiple accounts for the same symbol. Marks employer stock plan positions — excluded from concentration warnings; correct account attribution regardless of CSV row order. |
| `ACCOUNT_LABELS` | `rawid:FriendlyName` pairs, comma-separated. Maps raw CSV account IDs to display-friendly names shown in reports. |
| `MANAGED_ACCOUNTS` | Comma-separated list of account display names that are discretionary or advisor-managed. Flagged in analysis context and FA-discussion topics. |

### Paths and directories

| Variable | Default | Notes |
|----------|---------|-------|
| `INVESTOR_CLAW_PORTFOLIO_DIR` | `~/portfolios` | Directory scanned for portfolio CSV/XLS/XLSX files |
| `INVESTOR_CLAW_REPORTS_DIR` | `~/portfolio_reports` | Output directory for all generated artifacts |

### Local consultation model

| Variable | Default | Notes |
|----------|---------|-------|
| `INVESTORCLAW_CONSULTATION_ENABLED` | `false` | Set `true` to enable local consultative synthesis |
| `INVESTORCLAW_CONSULTATION_ENDPOINT` | `http://localhost:11434` | Ollama base URL |
| `INVESTORCLAW_CONSULTATION_MODEL` | `gemma4-consult` | Model name on the Ollama endpoint |

### EOD report delivery

| Variable | Notes |
|----------|-------|
| `EOD_EMAIL_TO` | Default recipient; overridden by `--email-to` flag |
| `INVESTOR_CLAW_EOD_GOG` | `true` to use `gog` transport by default |
| `INVESTOR_CLAW_GOG_ACCOUNT` | Google account identifier for `gog` sends |
| `SMTP_HOST` | SMTP relay hostname |
| `SMTP_PORT` | SMTP port (default: 587) |
| `SMTP_USER` | SMTP auth username |
| `SMTP_PASS` | SMTP auth password |
| `SMTP_FROM` | From address for SMTP sends |

---

## Output Model

InvestorClaw follows a dual-output pattern:

| Output | What it contains | Audience |
|--------|------------------|----------|
| `stdout` | Compact, token-aware JSON or human-readable command output | OpenClaw agent context |
| Disk artifact | Full JSON, CSV, or Excel output | Human review and downstream tools |

The agent reads stdout exclusively. Each compact payload includes a `_note` key pointing to the full artifact path. This keeps sessions well within the context window of any 128K+ model.

Full artifact names: `holdings.json`, `performance.json`, `bond_analysis.json`, `analyst_data.json`, `portfolio_news.json`, `portfolio_analysis.json`, `fixed_income_analysis.json`, `session_profile.json`.

---

## Choosing Your Operational LLM

InvestorClaw uses a single operational LLM for routing, analysis, and guardrail enforcement through OpenClaw. The right configuration depends on two things: **portfolio complexity** and **whether you have a local GPU available for consultation**.

### Does your portfolio need local enrichment?

Not every portfolio benefits equally from the local consultation model. The synthesis quality gap between cloud-only and hybrid configurations is driven by how much per-holding analyst data exists to enrich. ETFs and index funds have no individual analyst ratings — synthesis for an ETF-heavy portfolio is primarily allocation math and bond analytics, which cloud models handle well. Individual equities have per-symbol analyst consensus, earnings estimates, and price targets that the local model extracts and structures before synthesis runs.

| Portfolio type | Typical holdings | Account mix | Cloud-only quality | Local enrichment benefit |
|----------------|:----------------:|-------------|:-----------------:|:------------------------:|
| Simple — mostly ETFs + a few ESPPs | < 50 | 1–2 accounts | ✅ Acceptable | Low — ETFs carry no per-holding analyst ratings |
| Mixed — ETFs and individual equities | 50–150 | 2–3 accounts | ⚠️ Workable | Moderate |
| Complex — large individual equity portfolio, bonds, managed accounts | 150+ | Multiple account types | ❌ Shallow synthesis | High — the harness measured a 10–15× metric density gap |

**If your portfolio is mostly ETFs and index funds with a handful of ESPPs, cloud-only deployment is fine for an initial release.** The synthesis output is primarily about allocation percentages and sector distribution — data the operational model derives well without enrichment. The local consultation layer adds the most measurable value when there are many individual equities with distinct analyst coverage, price targets, and earnings data to enrich before synthesis runs.

---

### Profile 1 — canonical recommendation (hybrid)

**Operational LLM**: xAI Grok 4.1 Fast  
Model ID: `xai/grok-4-1-fast` (alias: `grok-reasoning`)

**Consultative LLM**: `gemma4-consult` on local Ollama (CERBERUS or equivalent ~16 GB VRAM GPU)

This is the recommended deployment for initial release. It is the configuration InvestorClaw was designed around and the one validated by the test harness. It gives:
- persistent-session context headroom (~2M tokens — no session truncation on large portfolios)
- per-holding analyst enrichment before synthesis, producing measurably denser output
- anti-fabrication controls (HMAC fingerprint chain, verbatim attribution, `is_heuristic=false`)
- local data residency — raw portfolio detail stays on-premise; the operational model sees only reduced artifacts
- zero marginal cost for the enrichment layer (local inference)

Why Grok 4.1 Fast specifically:
- handles long-lived, tool-heavy OpenClaw sessions well
- 2M context means even a fully-enriched 270-holding session never hits a limit
- agentic calibration is a better fit for InvestorClaw's multi-step workflow than models tuned for single-shot chat

> **Compliance note**: `xai/grok-4-1-fast` requires running `/portfolio update-identity` at the start of each session. Without this step, guardrail disclaimer compliance drops to near zero. This is an xAI quirk, not an InvestorClaw bug.

Why `gemma4-consult` specifically:
- runs at ~65 tok/s on a single RTX 4500 Ada or equivalent — fast enough to enrich 20 holdings in the background while the session continues
- the `gemma4-consult` Ollama variant uses a concise system prompt that prioritises structured analytical output over conversational filler
- validated end-to-end against InvestorClaw's tier-3 enrichment format; other models will likely work but are untested

**Hardware requirement**: any system with a GPU carrying ~10 GB of VRAM in the 16 GB VRAM class or better running Ollama. A Mac with 16 GB unified memory also works via Metal acceleration.

---

### Profile 2 — cloud-only deployment

**Honest quality advisory for complex portfolios**: if you have a large portfolio with many individual equity positions, bonds, and multiple account types, cloud-only synthesis will be shallower than the hybrid configuration. The harness measured 5–11 metric citations in cloud-only synthesis output vs. 120 in the hybrid configuration on an identical portfolio. This is not a model capability limitation — it is a data availability limitation. The cloud models are synthesising from thin heuristic analyst summaries; the hybrid configuration synthesises from per-holding enriched records. No frontier model, regardless of cost, can close that gap without the enrichment step.

**For simple portfolios this caveat does not apply.** If your holdings are primarily ETFs, broad index funds, and a small number of ESPPs, there is little per-holding analyst data to enrich in the first place. Cloud-only output quality for allocation analysis, bond analytics, and sector breakdown is good.

**Recommended cloud-only models** (ranked by harness performance for complex portfolios):

1. **xAI Grok 4.1 Fast** — `xai/grok-4-1-fast` (~2M context) — primary recommendation even without local enrichment; best agentic session calibration of the group
2. **xAI Grok 4.20** — `xai/grok-4.20-0309-non-reasoning` — best synthesis density of any cloud-only configuration tested; uniquely added cross-holding news sentiment in harness runs
3. **Together AI / Llama 4 Maverick** — `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` (~1M context) — good cost/context ratio; untested in harness
4. **Together AI / Qwen3-235B** — `together/Qwen/Qwen3-235B-A22B-FP8-tput` (262K context) — strong reasoning; throughput-optimized; untested in harness
5. **OpenAI GPT-5.4** — `openai/gpt-5.4` (~272K context) — produced shallower synthesis than the default baseline in harness testing despite higher cost; see [Benchmark Results](#benchmark-results--harness-v612-2026-04-13)
6. **Google Gemini 3.1 Pro** — `google/gemini-3.1-pro-preview` (~1M context) — diverged to generic educational content in the synthesis step during harness testing; individual commands worked correctly; not recommended as primary for complex portfolios

Important cost guidance:
- frontier models are often reasonable for **specific InvestorClaw sessions**
- they are usually **too expensive to leave as the primary always-on operational model** for all OpenClaw activity
- a good pattern is to keep a cheaper general OpenClaw default and switch to a frontier model only for high-value InvestorClaw workflows

> **Do not use GPT-4.1-nano** (`openai/gpt-4.1-nano`). Its Tier 1 rate limit is **30K TPM shared across all OpenClaw session activity**. Any concurrent agentic work exhausts the budget before a full portfolio analysis completes.

### Profile 3 — getting started / modest single-system deployment

If you are new to InvestorClaw or running a modest single-machine OpenClaw setup:

1. **Start with Profile 2** using `xai/grok-4-1-fast` as the operational model. Run through the basic portfolio workflows and assess whether synthesis depth meets your needs.
2. **Add local enrichment when ready**: if you have or acquire a compatible GPU, install Ollama, pull `gemma4-consult`, and set `INVESTORCLAW_CONSULTATION_ENABLED=true` in `.env`. The enrichment layer activates automatically on the next session.
3. **Use premium frontier models selectively** for high-value InvestorClaw sessions rather than as the always-on OpenClaw default.

This path lets you get value immediately without hardware commitment, and upgrade to the hybrid architecture without any code changes — just a configuration update.

### Why this recommendation structure exists

InvestorClaw is not a single-shot prompt workload. It behaves like a persistent agentic application: repeated tool calls, guardrail text, report handling, compact artifact generation, and follow-up analysis all accumulate inside the same working session.

In practice, the choice is about system behavior, not benchmark vanity:
- **Persistent-agent friendliness**: long sessions need context headroom and throughput, not just raw benchmark scores
- **Operational cost discipline**: compact artifacts and local consultation help avoid burning frontier-model tokens unnecessarily
- **Selective premium usage**: the most expensive frontier models are best reserved for the sessions where their extra capability is worth the cost

Supporting background: https://techbroiler.net/openclaw-backend-optimization-groq-vs-claude-for-persistent-ai-agents/

### Fast inference: Groq (Llama)

For applications where latency matters more than context depth — dashboards, quick status checks, polling loops — Groq provides exceptionally fast Llama inference:

| Model | Context | Use case |
|-------|---------|---------|
| `groq/llama-3.3-70b-versatile` | 128K | Best Groq quality; small–medium portfolios |
| `groq/llama-3.1-8b-instant` | 128K | Fastest response; limited reasoning depth |
| `groq/openai/gpt-oss-120b` | 128K | OpenAI OSS 120B via Groq |
| `groq/openai/gpt-oss-20b` | 128K | OpenAI OSS 20B via Groq |

> 128K context caps these to small-to-medium portfolios. Not suitable for multi-account or fully-enriched sessions.

### On-Premise: NVIDIA NIM and NemoClaw

For organizations that cannot send portfolio data to external APIs:

- Model ID: `nvidia/nemotron-3-super-120b-a12b` (256K context) via NVIDIA NIM inference
- **NemoClaw** is NVIDIA's hardened OpenClaw distribution for on-premise and air-gapped deployments; InvestorClaw can be paired with NemoClaw-managed infrastructure and NVIDIA Nemotron models

See the [NemoClaw documentation](https://github.com/NVIDIA/NemoClaw) for deployment details.

### Provider comparison

| Model | Context | Provider | Notes |
|-------|---------|---------|-------|
| `xai/grok-4-1-fast` | ~2M | xAI | **Primary recommendation**; needs `update-identity` each session |
| `google/gemini-3.1-pro-preview` | ~1M | Google | Best high-context alternative; reasoning enabled |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | ~1M | Together AI | Good cost/context ratio |
| `together/Qwen/Qwen3-235B-A22B-FP8-tput` | 262K | Together AI | Strong reasoning; throughput-optimized |
| `openai/gpt-5.4` | ~272K | OpenAI | Strong reasoning; verify session fits |
| `openai/gpt-5.3-chat-latest` | ~400K | OpenAI | Verify session fits |
| `nvidia/nemotron-3-super-120b-a12b` | 262K | NVIDIA NIM | On-premise / air-gapped; reasoning enabled |
| `groq/llama-3.3-70b-versatile` | 128K | Groq | Fast inference; small portfolios only |
| `openai/gpt-4.1-nano` | ~1M | OpenAI | Not recommended — 30K TPM Tier 1 limit |

---

## Benchmark Results — Harness V6.1.2 (2026-04-13)

These results come from a full run of the InvestorClaw Test Harness V6.1.2 against a live 270-holding, $2.59M multi-account portfolio. The harness exercises all core workflows (holdings, analysis, performance, bonds, synthesis, lookup, export) across five model configurations and scores the output across 14 quality-control dimensions.

### Why these results are surprising

The headline finding is that **a local 10B-parameter model running on a single GPU, combined with the default operational LLM, produces information density an order of magnitude higher than the top frontier models used alone**. This is not because the local model is smarter — it is because it operates at the *data layer*, not the synthesis layer. By enriching analyst records before the operational model ever runs synthesis, the combined configuration changes what the model is writing *about*, not how well it writes.

### Test configuration

| Configuration | Operational LLM | Enrichment model | Mode |
|---------------|-----------------|------------------|------|
| **Combined (recommended)** | `xai/grok-4-1-fast-reasoning` | `gemma4-consult` (CERBERUS, Ollama) | Tier-3 enriched |
| True baseline | `xai/grok-4-1-fast-reasoning` | none | Heuristic |
| WF36 | `openai/gpt-5.4` | none | Heuristic |
| WF37 | `xai/grok-4.20-0309-non-reasoning` | none | Heuristic |
| WF38 | `google/gemini-3.1-pro-preview` | none | Heuristic |

### Information density scores (W6 synthesis output)

Scores are measured against the portfolio synthesis command output — the highest-value single response in a typical InvestorClaw session.

| Metric | Combined (grok + CERBERUS) | Grok 4.20 | True baseline | GPT-5.4 | Gemini 3.1 Pro |
|--------|:--------------------------:|:---------:|:-------------:|:-------:|:--------------:|
| **QC3** Ticker mentions | **8** | 8 | 7 | 2 | 0 |
| **QC4** Metric citations | **120** | 11 | 8 | 6 | 5 |
| **QC5** Word count | **1,184** | 260 | 200 | 180 | 175 |
| **QC8** `is_heuristic=false` | **✅** | ✗ | ✗ | ✗ | ✗ |
| **QC9** `synthesis_basis=enriched` | **✅** | ✗ | ✗ | ✗ | ✗ |
| **QC10** HMAC fingerprint | **✅** | ✗ | ✗ | ✗ | ✗ |
| **QC11** `verbatim_required=True` | **✅** | ✗ | ✗ | ✗ | ✗ |
| **QC12–14** All commands exit 0 | **✅** | ✅ | ✅ | ✅ | ✅ |

**QC4 amplification**: the combined config produces 120 metric citations in the synthesis response vs. 5–11 for any premium-only configuration. The local enrichment model generates per-symbol insights, key metrics, and risk assessments for 20 holdings before the synthesis pass runs — the operational model then synthesises those pre-computed results rather than inferring from heuristic summaries.

### Anti-fabrication properties (combined config only)

The tier-3 enrichment path adds audit controls that no cloud-only configuration provides:

- **HMAC fingerprint chain** — each enriched record gets a 16-character hex fingerprint; the session accumulates a chained fingerprint across all enriched symbols, allowing post-hoc verification that synthesis content matches the enrichment artifacts it claims to summarise.
- **`verbatim_required=True` + attribution** — enriched analyst quotes carry a verbatim flag and source attribution; the synthesis layer is constrained to cite rather than paraphrase.
- **`is_heuristic=false`** — signals to downstream consumers that synthesis was produced from enriched model inference, not keyword matching.

These controls are absent in all cloud-only configurations regardless of model capability.

### Premium model ranking (cloud-only, no enrichment)

When tier-3 enrichment is not available and the operational model must do all synthesis work directly, the ranking from this harness run is:

**1. Grok 4.20** (`xai/grok-4.20-0309-non-reasoning`) — best premium-only result. Matched CERBERUS on ticker density (QC3=8), highest metric count of the cloud-only group (QC4=11), and uniquely added cross-holding news sentiment correlation (TXG, AMD, AEIS, AIR) that no other model surfaced. Synthesis remained portfolio-specific throughout all workflow steps.

**2. grok-4-1-fast-reasoning (true baseline)** — marginally below Grok 4.20 on density metrics (QC3=7, QC4=8) but noticeably more compact. No padding. Functions as the reliable operational default.

**3. GPT-5.4** — underperformed relative to its reputation in this workload. Synthesis collapsed to high-level talking points with only 2 ticker mentions and 6 metric citations — worse than the free baseline. Not worth the cost premium for InvestorClaw sessions specifically.

**4. Gemini 3.1 Pro** — failed to engage with portfolio-specific synthesis. Produced a generic allocation scenario table (Conservative/Balanced/Aggressive Growth) with zero ticker mentions. The model answered a different question than was asked. Individual commands (holdings, bonds, lookup) all worked correctly — the failure was specific to the synthesis routing step.

> **Important caveat**: these are single-session results on one portfolio. Model behavior varies by prompt shape, session length, and provider updates. Treat the rankings as an informed starting point, not a permanent ordering.

### The core finding

**The enrichment layer, not the operational model, is the primary driver of synthesis quality.** Switching from the default operational model to any premium frontier model produces at most a small improvement in ticker density and a modest improvement in phrasing quality. Switching from heuristic mode to tier-3 enrichment produces a 10–15× increase in metric density and adds anti-fabrication guarantees that no amount of model capability can replicate.

This is consistent with the original design intent: the consultative model is responsible for *data enrichment*; the operational model is responsible for *session management and synthesis routing*. The harness results quantify that split empirically for the first time.

### What this means for your deployment

The benchmark portfolio — 270 holdings, 38 bond positions, 8 accounts, multiple managed accounts and ESPPs — represents a complex, real-world scenario. The results are most relevant to users in that tier.

**If your portfolio is complex** (many individual equities, multiple account types, significant bond positions): the harness results apply directly. Cloud-only synthesis will be measurably shallower. Profile 1 is strongly recommended. The cost of a GPU node capable of running `gemma4-consult` is small relative to the portfolio scale where enrichment matters most.

**If your portfolio is simple** (mostly ETFs, 1–2 accounts, a handful of ESPPs): the metric density gap narrows significantly. ETFs do not have individual analyst ratings, so there is less to enrich in the first place. Cloud-only deployment with `xai/grok-4-1-fast` is a reasonable starting point and the harness results should not alarm you. Start with Profile 2 and upgrade to Profile 1 if you find the synthesis depth insufficient.

**On premium frontier models specifically**: the harness result for GPT-5.4 scoring below the free baseline — and Gemini 3.1 Pro producing zero ticker mentions in synthesis — reflects real behaviour on this specific workload, not a general capability assessment. These models are capable systems that may behave differently on other portfolio shapes or with different prompt structures. The finding is that paying more for the operational model is a poor substitute for enriching the data the model synthesises from.

### Reproducibility

The harness is at `investorclaw_harness_v611.txt` in the repository root. To reproduce:

```bash
# Requires OpenClaw gateway running with investorclaw plugin loaded
# Requires CERBERUS (or equivalent Ollama host) for tier-3 enrichment steps
# Full run covers 39 workflow checkpoints across 5 phases
```

---

## Market Data Sources

InvestorClaw supports multiple market data providers. No single provider covers every data type at every price point — the sections below explain what each provider actually delivers, where the gaps are, and which configuration to use.

### Provider capabilities (honest assessment)

All rows reflect live testing or published free-tier specs. "Tested" means a real API call was made against a live portfolio.

| Provider | Quotes | History | News | Analyst | Free tier | Paid tier |
|----------|--------|---------|------|---------|-----------|-----------|
| **Massive** | ✅ Batch — 268ms/215 symbols (tested) | ✅ Full OHLCV | ✅ | ❌ | Prev-day only | Starter plan — affordable, recommended |
| **yfinance** | ✅ Batch, fast | ✅ | ✅ | ✅ | Unlimited — no key | No paid tier exists |
| **Finnhub** | ✅ ~8s/215 symbols (tested) | ❌ 403 on free | ✅ (tested) | ⚠️ unreliable on free | 60 req/min, no daily cap | ~$3,500/month — enterprise only |
| **Alpha Vantage** | ✅ Sequential only | ✅ Adjusted EOD | ❌ | ✅ Earnings proxy | 25 req/day (5/min) | Tiered paid plans |
| **NewsAPI** | ❌ | ❌ | ✅ | ❌ | 100 req/day | Tiered paid plans |

**Key gaps no free provider fills cleanly:**
- Reliable analyst buy/sell/hold consensus: yfinance works but is unofficial; Finnhub free returns placeholder data for many tickers
- Real-time batch quotes at speed: requires Massive Starter or better
- Historical OHLCV beyond Alpha Vantage's 25-req/day limit: requires Massive Starter

**Notes on providers not listed:**
- **Finnhub paid**: ~$3,500/month enterprise pricing — no personal tier, not a realistic upgrade path
- **Financial Modeling Prep (FMP)**: Free tier was gutted in August 2025 migration; quotes, history, and news all return 402 on new accounts. Not supported.
- **Google Finance, Bing**: No usable API for either. Google's official finance API was discontinued in 2012; Bing Search API shut down in 2025.
- **IEX Cloud**: Shut down August 2024. Do not use.

### Recommended configurations

#### Config A — No API keys (zero cost)

Uses yfinance for everything. Works immediately with no registration. Suitable for getting started and testing the skill before committing to any API keys.

```bash
INVESTORCLAW_PRICE_PROVIDER=yfinance
```

**Caveat**: yfinance is an unofficial Yahoo Finance scraper with no SLA. Yahoo has broken it without notice before. There is no official paid Yahoo Finance API — Yahoo discontinued their developer API in 2017 and never replaced it. For personal use it is fine; treat it as a convenience, not infrastructure.

---

#### Config B — Free with API keys (better reliability)

Splits responsibilities across free tiers: Finnhub for real-time quotes and news, Alpha Vantage for historical prices, yfinance as the analyst and fallback layer.

```bash
INVESTORCLAW_PRICE_PROVIDER=auto
INVESTORCLAW_FALLBACK_CHAIN=finnhub,alpha_vantage,yfinance
FINNHUB_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_key_here
NEWSAPI_KEY=your_key_here        # optional — adds supplemental news sources
```

Register free keys at:
- Finnhub: https://finnhub.io/register (60 req/min, no daily cap)
- Alpha Vantage: https://www.alphavantage.co/support/#api-key (25 req/day, 5/min)
- NewsAPI: https://newsapi.org/register (100 req/day)

**What this buys over Config A**: Finnhub quotes are faster and more reliable than yfinance (~8s vs variable for 215 symbols); Alpha Vantage provides officially-licensed adjusted historical prices. Analyst ratings still fall back to yfinance — no free provider delivers reliable consensus ratings.

**Limit to watch**: Alpha Vantage's 25 req/day cap. Historical analysis on large portfolios can exhaust this quickly. yfinance picks up the slack but with unofficial data.

---

#### Config C — Massive Starter (recommended for regular use)

Massive (polygon.io-compatible) handles real-time quotes and full OHLCV history on a single Starter plan key. Finnhub free adds news. yfinance covers analyst ratings, which no paid provider at a personal price point provides.

```bash
INVESTORCLAW_PRICE_PROVIDER=massive
MASSIVE_API_KEY=your_key_here
FINNHUB_KEY=your_key_here        # free — adds news aggregation alongside Massive
```

Live benchmark on Starter plan: **268ms for a 215-symbol portfolio** via the batch snapshot endpoint.

**What Massive covers**: real-time quotes (batch), full OHLCV history, news.  
**What still uses yfinance**: analyst ratings — Massive does not provide analyst recommendations.

---

## Local Consultation Model (Optional, Strongly Recommended)

InvestorClaw supports a two-layer architecture:

1. **Operational LLM** (usually cloud) — handles routing, conversation, orchestration, and guardrail enforcement
2. **Consultation model** (usually local Ollama) — performs structured portfolio synthesis before the operational model sees the reduced result

The consultation model is **not a hard requirement**. InvestorClaw can run without it. But it is **strongly recommended** because the skill was deliberately designed so that consultation improves determinism, lowers cloud token pressure, and narrows what the operational model is allowed to do.

### Why the consultation layer exists

When consultation is enabled, the local model receives the relevant structured portfolio data and produces bounded synthesis fields: `synthesis`, `key_insights`, `risk_assessment`. The operational LLM then consumes that reduced result rather than performing the same free-form reasoning directly over the raw portfolio payload.

This architecture improves behavior in four ways:

- **More deterministic analysis flow**: Python computes the structured facts; the consultation model synthesizes against that bounded input instead of asking the operational LLM to improvise from scratch
- **Quote-first behavior**: when consultative output is present, the operational LLM is expected to quote or relay that result rather than invent fresh observations on top of it
- **Better privacy boundaries**: raw portfolio detail can stay local to your infrastructure when consultation runs on your own Ollama host
- **Lower context and token cost**: the cloud operational model sees compact downstream artifacts, not the entire raw working set

### How context preservation works

InvestorClaw was intentionally designed so the LLM does **not** have to ingest every full raw artifact on every turn:

1. Full analysis artifacts are written to disk under `~/portfolio_reports/.raw/`
2. Compact summaries are emitted to stdout and written to agent-readable summary files
3. The agent uses those compact artifacts by default
4. If a specific detail is needed later, the lookup command extracts only the requested slice from the raw files

### Recommended consultation setup

Enable via `.env`:
```bash
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

`gemma4-consult` is the recommended model — a tuned Ollama derivative of `gemma4:e4b` optimized for fast consultative Q&A (num_ctx=2048, num_predict=600, ~65 tok/s on RTX Ada). Create it with:

```bash
ollama create gemma4-consult -f docs/gemma4-consult.Modelfile
```

**Hardware requirements**: 12+ GB VRAM, CUDA compute capability >= 8.0 (RTX 30xx / A-series / Ada Lovelace or newer), Ollama >= 0.20.x.

Other tested models: `gemma4:e4b`, `nemotron-3-nano`, `qwen2.5:14b`. Run `/portfolio ollama-setup` to auto-detect available models on your Ollama endpoint.

---

## Configuration Examples

### Example 1 — recommended hybrid default

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "xai/grok-4-1-fast"
      }
    }
  }
}
```

Pair with `.env`:
```bash
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
```

### Example 2 — premium cloud-only session override

Use a stronger frontier model for a specific high-value InvestorClaw session, then switch back.

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "google/gemini-3.1-pro-preview"
      }
    }
  }
}
```

### Example 3 — modest single-system starting point

Start with Grok as the operational model and add the consultation layer later when local inference is available:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "xai/grok-4-1-fast"
      }
    }
  }
}
```

---

## Data Locality and Privacy Model

InvestorClaw's privacy boundary depends on your model architecture.

**Without a local consultation model**
- portfolio-derived summaries and analysis context may be sent to the configured cloud operational LLM
- raw working files still remain on your local system
- the operational model may have to perform more synthesis directly

**With a local consultation model**
- structured portfolio analysis is synthesized locally first
- raw portfolio detail can remain on your own infrastructure during the consultative phase
- the cloud operational LLM is limited to compact downstream artifacts and quoted consultative output

**Practical guidance**
- keep `~/portfolios` and `~/portfolio_reports` on trusted local storage
- use the consultation layer if you want stronger locality boundaries
- choose on-premise inference or private infrastructure where your requirements demand it
- treat cloud-model usage as a deliberate architectural choice, not an invisible default

---

## Session Size and Context Planning

The estimates below are **planning guidance**, not hard limits. InvestorClaw's compact-output design keeps operational context much smaller than raw artifact size by emitting compact stdout payloads, preserving full reports on disk, and using targeted extraction when a later turn needs more detail.

Actual session pressure depends on: total positions, equities vs bonds mix, analyst/news enrichment breadth, whether consultation is enabled, compact vs verbose workflows, and follow-up turn count.

### Portfolio size tiers

| Tier | Size | Expected behavior |
|------|------|------------------|
| Small | up to ~50 positions | Full compact command pass comfortable for most operational models |
| Medium | ~50–200 positions | Compact mode strongly preferred; hybrid Grok + consultation is the preferred deployment |
| Large | 200+ positions | Long-session management, compact artifacts, and selective extraction become essential |

### Operational guidance by profile

- **Hybrid Grok + local consultation**: best overall fit for repeated full command passes across all three portfolio tiers
- **Cloud-only premium frontier models**: best reserved for specific high-value InvestorClaw sessions, especially medium and large portfolios
- **Modest single-system deployments**: start in compact mode, avoid unnecessary verbose passes, and add the consultation layer when practical

---

## Authority Model: Operational vs Consultative Output

When consultation is enabled, InvestorClaw deliberately separates **operational orchestration** from **consultative synthesis**.

**When consultation is enabled**: the operational LLM is expected to **quote, relay, or frame** the consultative result rather than invent a fresh competing portfolio judgment. The operational model behaves as the messenger and orchestrator, not as a second independent portfolio analyst rewriting the result from scratch.

**When consultation is not enabled**: the operational LLM does more direct synthesis work itself; stronger frontier cloud models become more attractive for demanding sessions because there is no local synthesis layer narrowing the task.

**Why this split exists**: to improve determinism, preserve context budget, keep raw artifacts out of repeated conversational turns, and reduce the chance that two different LLM stages make competing observations about the same portfolio state.

---

## Example End-to-End Workflow

1. Put portfolio files in `~/portfolios`
2. Run setup / discovery to normalize the inputs
3. Generate holdings, performance, bond, analyst, and news outputs
4. Full artifacts written to `~/portfolio_reports/.raw/`
5. Compact summaries emitted to stdout and agent-readable summary files
6. If consultation is enabled, synthesize locally before the operational model frames the result
7. Use lookup extraction later when a follow-up question needs a specific symbol or detail

This workflow is the core of InvestorClaw's design: raw artifacts on disk preserve completeness; compact artifacts in chat preserve context budget; lookup extraction preserves precision without reloading everything; consultation-first synthesis preserves more disciplined model behavior when the optional local layer is enabled.

---

## FINOS CDM Scope

InvestorClaw uses **FINOS CDM 5.x concepts and canonical structured models** as part of its internal normalization and reporting approach.

### What InvestorClaw uses CDM for
- canonical normalization of holdings and portfolio data
- structured analysis payloads and downstream report generation
- schema discipline for portfolio analytics workflows
- reducing drift between internal models, serialized artifacts, and follow-on processing

### What InvestorClaw does not claim
- a full end-to-end FINOS CDM implementation across the entire trade lifecycle
- complete institutional post-trade, operations, settlement, or event-processing coverage
- replacement for an OMS, EMS, broker back office, or enterprise portfolio accounting system
- regulatory or compliance certification merely because CDM-inspired structures are used internally

In short: InvestorClaw uses FINOS CDM as a practical canonical data discipline for portfolio analysis, not as a claim that the project implements the full CDM universe.

---

## Limitations and Non-Goals

### Non-goals
- it is **not** a trading execution system
- it is **not** an OMS, EMS, or broker back office
- it is **not** a substitute for a financial advisor, tax professional, or legal professional
- it is **not** a guarantee of market-data completeness or correctness
- it is **not** a claim of full institutional workflow coverage just because it uses CDM-inspired structures

### Practical limitations
- output quality depends on portfolio input quality and upstream market-data availability
- larger portfolios still require disciplined compact-session usage even with the context-preserving design
- cloud-only deployments push more synthesis responsibility onto the operational model
- optional consultation improves determinism and cost control, but still depends on model quality and local infrastructure health

---

## Best Practices

### Model selection
- Use `xai/grok-4-1-fast` for most deployments — ~2M context eliminates truncation risk
- If you choose a smaller cost-oriented cloud model, expect tighter rate-limit and session-budget constraints during multi-command use
- All models with 128K+ context windows are compatible; 200K+ is recommended; 1M+ for large multi-account portfolios

### OpenClaw configuration
- Bind the OpenClaw gateway to loopback (`127.0.0.1:18789`) only — do not expose to LAN unless behind a firewall; portfolio data passes through this gateway
- Keep API keys in `.env` or OpenClaw's skill settings — never commit them to version control
- Use NemoClaw-managed infrastructure, a private Ollama instance, or another private inference path when portfolio data must remain on-premise

### Portfolio files
- Store portfolio CSVs in a dedicated directory outside your git repository
- Set `INVESTOR_CLAW_PORTFOLIO_DIR` to point to that directory
- InvestorClaw scrubs PII (account numbers, SSNs, credit card patterns) from CSV columns on load

### Session management
- Run `/portfolio session` at the start of each session to calibrate the context budget
- Use `--verbose` for diagnostics; omit it for production to keep output compact

---

## Requirements

- Python 3.9+
- OpenClaw >= 2026.0.0
- API keys (all optional, all have free tiers):
  - [Finnhub](https://finnhub.io/register) — real-time quotes and analyst ratings (recommended primary)
  - [NewsAPI](https://newsapi.org/register) — portfolio news correlation
  - [Massive](https://polygon.io/dashboard/signup) (`MASSIVE_API_KEY`) — real-time quotes and historical OHLCV (polygon.io-compatible)
  - [Alpha Vantage](https://www.alphavantage.co/support/#api-key) — adjusted historical prices (500 req/day free)
  - [FRED](https://fred.stlouisfed.org/docs/api/api_key.html) — Treasury benchmark yields
- Without any API keys, InvestorClaw falls back to `yfinance` for quotes — see [Market Data Sources](#market-data-sources) for caveats

### Practical installation requirements

**Minimum software**
- Python 3.9+
- OpenClaw 2026.4.x (tested series for the current project state)
- network access to your chosen operational LLM provider
- read/write access to `~/portfolios` and `~/portfolio_reports`

**Recommended software**
- Python virtual environment for local testing and regression work
- `pytest` plus `requirements-dev.txt` when validating changes
- Ollama only if you want the optional local consultation layer

**Compatibility note**
- InvestorClaw has been tested on **OpenClaw 2026.4.x**
- it has **not** been broadly validated on older OpenClaw releases, OpenClaw derivatives, or other agentic systems that happen to support skill-like plugins

**Minimum hardware**
- modern 64-bit CPU
- enough RAM for Python, parsing, and report generation on personal portfolio datasets

**Recommended hardware**
- workstation-class CPU and 16 GB+ RAM for smoother large-portfolio workflows
- a local GPU or accelerator only if you want fast consultative inference through Ollama

**Hardware validation note**
- development and testing were performed on **Apple Silicon Mac hardware** and **NVIDIA-backed Linux hardware**
- broader local-acceleration paths such as AMD, Intel, or other integrated/APU GPU workflows are plausible but were **not** part of the direct validation performed for this project

### Tested environment

InvestorClaw was developed and tested on the following reference systems:

**Developer Workstation**
- OS: macOS 26.5 (build 25F5042g)
- CPU: Apple M1 Max (10-core: 8 performance + 2 efficiency)
- RAM: 32 GB unified memory
- Python: 3.14.3
- OpenClaw: 2026.4.9 (0512059)
- role: primary development, control-path testing, OpenClaw-side workflow validation

**Inference Host**
- OS: Debian GNU/Linux 13 (trixie)
- CPU: AMD Ryzen Threadripper PRO 5945WX (12-core, 24 threads)
- RAM: 128 GB
- GPU: NVIDIA RTX 4500 Ada Generation (23034 MiB VRAM), driver 595.58.03
- Python: 3.13.5
- Ollama: 0.20.3
- role: local consultation model and GPU-backed enrichment testing

Observed consultation models on the Inference Host: `gemma4-consult`, `gemma4:e4b`, `gemma4:e2b`, `nemotron-3-nano:30b-a3b-q4_K_M`

---

## Who This Is For

InvestorClaw is primarily for:
- individual investors who want agentic Q&A over their own portfolio data
- advanced self-directed investors who want deeper bond, analyst, news, and allocation analysis
- OpenClaw users who want a data-intensive reference skill rather than a toy wrapper
- operators who are comfortable with structured files, reports, and multi-step workflows

InvestorClaw is probably **not** the best fit if you want:
- a zero-setup retail finance app
- direct trading or order execution
- a replacement for your broker portal
- institutional OMS / EMS / post-trade infrastructure
- guaranteed low-complexity operation without any interest in setup, configuration, or data pipelines

---

## What Gets Installed

| Path | Purpose |
|------|---------|
| `investorclaw.py` | Entry point — all commands run through here |
| `SKILL.md` | Skill manifest loaded by OpenClaw into agent context |
| `commands/` | One Python analysis script per command |
| `config/` | Config loading, arg synthesis, path resolution, help text |
| `models/` | Portfolio, holdings, routing, and context models |
| `providers/` | External market and symbol data providers |
| `rendering/` | Compact serializers, consultation cards, disclaimers, progress |
| `runtime/` | Router, environment bootstrap, subprocess runner |
| `services/` | Consultation policy, portfolio consolidation, PDF extraction, utilities |
| `setup/` | First-run helpers, installer, setup wizard, identity updater |
| `internal/` | Tier-3 enrichment internals |
| `data/` | Guardrails and symbol/reference data |
| `tests/` | Unit and contract tests |
| `pipeline.py` | Full pipeline entry for multi-step analysis |
| `~/portfolios/` | Default input directory for your portfolio CSV/XLS/XLSX files |

**Never committed:**
- `.env` — your API keys; create from `.env.example`
- `~/portfolios/*` — your personal holdings data
- `~/portfolio_reports/` — generated output files (written at runtime to `$INVESTOR_CLAW_REPORTS_DIR`)

---

## Security

InvestorClaw implements several security measures:

- **PII scrubbing**: credit card numbers, SSNs, and account IDs are redacted from CSV columns before processing
- **Prompt injection defense**: portfolio text columns are scanned for injection patterns before data is passed to the LLM
- **Math verification**: all financial calculations are performed by deterministic Python scripts — the LLM never computes portfolio math in-context
- **Data locality**: raw CSV data is never sent to external APIs; only computed summaries are passed to the cloud LLM
- **Guardrails**: `data/guardrails.yaml` enforces educational-only output, blocks suitability assessments, and prevents specific investment recommendations

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
| `services/` | Consultation policy, portfolio consolidation, PDF extraction, utilities |
| `setup/` | First-run, installer, setup wizard, identity updater |
| `internal/` | Tier-3 enrichment internals |
| `data/` | Guardrails and symbol/reference data |
| `tests/` | Unit and contract tests |
| `pipeline.py` | Full pipeline entry for multi-step analysis |

---

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
python3 tests_smoke.py
```

---

## Design Intent

InvestorClaw is a reference design for a **data-intensive, stateful agentic skill** in OpenClaw. It is intended as a worked example of how to combine:

- compact agent-facing outputs
- raw artifact preservation on disk
- deterministic downstream processing
- optional local consultative LLMs
- financial guardrails and educational-only output policy
- multi-step setup, routing, and report-generation flows

In other words, this skill is meant to show what a production-oriented OpenClaw skill looks like when the workload is materially more complex than a thin command wrapper or single-script utility.

> **Ecosystem maturity note**: InvestorClaw sits near the upper end of current OpenClaw skill complexity. Some of its design choices reflect not only the needs of portfolio analysis, but also the reality that the broader agentic skill ecosystem is still maturing around patterns for compact context, raw artifact preservation, consultation-model authority boundaries, and operational trust controls.

### Why this exists

InvestorClaw was built to address a gap in OpenClaw skill development. Financial data sources and portals already exist — Yahoo Finance, broker portals, and market-data APIs can all provide pieces of the picture — but they generally do not provide the same style of **agentic question-and-answer workflow** that OpenClaw users expect: a persistent assistant that can inspect portfolio artifacts, run analysis steps, preserve context across turns, and answer follow-up questions coherently.

InvestorClaw is intended to help bridge that gap. It does not replace broker systems or financial data vendors. Instead, it provides an OpenClaw-native layer that can combine portfolio files, market data, bond analytics, consultative synthesis, and guarded educational responses in one place.

### Perspective behind the design

InvestorClaw was shaped by practical experience across enterprise IT, AI systems, and financial-services environments. Its architecture reflects concerns that are common in those settings: canonical data normalization, operational resilience, auditability, context discipline, model-boundary control, and a careful distinction between analytical assistance and regulated financial advice.

That perspective is part of why the project emphasizes compact agent outputs, raw artifact preservation, deterministic downstream processing, explicit deployment tradeoffs, and conservative trust-boundary language instead of treating portfolio analysis as just another lightweight prompt wrapper.

InvestorClaw is substantially more complex than a typical lightweight ClawHub skill. It combines portfolio file discovery and normalization, multi-step analysis pipelines, compact-vs-full artifact generation, installer and setup flows, guardrail enforcement and disclaimer wrapping, optional local consultative LLM orchestration, and report persistence and downstream file workflows.

That complexity is intentional, but it means installation, testing, and release expectations should be closer to a small application than to a trivial agent tool plugin. At the same time, the skill was deliberately shaped around **context preservation** and **operational cost control**: compact stdout outputs keep agent context pressure lower than full raw report emission; full artifacts are written to disk for downstream use; the optional consultation layer can offload synthesis locally before the cloud operational model sees only reduced summaries.

Although development and validation were done on relatively powerful systems, InvestorClaw is intended to remain usable on a **modest single-system OpenClaw deployment** as well — a Mac running OpenClaw locally, or a Linux workstation with a local GPU in roughly the 16 GB VRAM class for consultation and enrichment workloads.

---

## Branding

- Primary logo: `assets/investorclaw-logo.png`
- Consultation cards embed the logo automatically when the asset is present

---

## Compliance

**NOT INVESTMENT ADVICE.** InvestorClaw provides educational portfolio analysis only. It is not a substitute for professional financial advice and does not assess personal risk tolerance, goals, or investment suitability.

## License

MIT — see [LICENSE](LICENSE).
