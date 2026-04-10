# InvestorClaw

<p align="center">
  <img src="https://raw.githubusercontent.com/perlowja/InvestorClaw/main/assets/investorclaw-logo.png" alt="InvestorClaw Logo" width="200"/>
</p>

Portfolio analysis skill for OpenClaw agents. **v1.0.0** | FINOS CDM 5.x | MIT License

Provides holdings snapshots, performance metrics, bond analytics, analyst ratings, portfolio news, and CSV/Excel exports — with built-in financial advice guardrails that enforce educational-only output.

> **Naming note**: the package id is `investorclaw` (used by the ClawHub marketplace and `openclaw.plugin.json`). The OpenClaw invocation command is `/portfolio` — that is what users type at the prompt. Both names are intentional.

---

## Branding

- Primary logo: `assets/investorclaw-logo.png`
- Consultation cards embed the logo automatically when the asset is present

## Design intent

InvestorClaw is our reference design for a **data-intensive, stateful agentic skill** in OpenClaw. It is intended as a worked example of how to combine:

- compact agent-facing outputs
- raw artifact preservation on disk
- deterministic downstream processing
- optional local consultative LLMs
- financial guardrails and educational-only output policy
- multi-step setup, routing, and report-generation flows

In other words, this skill is meant to show what a production-oriented OpenClaw skill looks like when the workload is materially more complex than a thin command wrapper or single-script utility.

> **Ecosystem maturity note**: InvestorClaw sits near the upper end of current OpenClaw skill complexity. Some of its design choices reflect not only the needs of portfolio analysis, but also the reality that the broader agentic skill ecosystem is still maturing around patterns for compact context, raw artifact preservation, consultation-model authority boundaries, and operational trust controls.

## Why this exists

InvestorClaw was built to address a gap we observed in OpenClaw skill development. We did not find a comparable skill that handled **general financial-market questions, bond analysis, and personal portfolio queries** inside a single agentic workflow.

Financial data sources and portals already exist, of course. Yahoo Finance, broker portals, and market-data APIs can all provide pieces of the picture. But they generally do not provide the same style of **agentic question-and-answer workflow** that OpenClaw users expect: a persistent assistant that can inspect portfolio artifacts, run analysis steps, preserve context across turns, and answer follow-up questions coherently.

InvestorClaw is intended to help bridge that gap. It does not replace broker systems or financial data vendors. Instead, it provides an OpenClaw-native layer that can combine portfolio files, market data, bond analytics, consultative synthesis, and guarded educational responses in one place.

## Perspective behind the design

InvestorClaw was shaped by practical experience across enterprise IT, AI systems, and financial-services environments. Its architecture reflects concerns that are common in those settings: canonical data normalization, operational resilience, auditability, context discipline, model-boundary control, and a careful distinction between analytical assistance and regulated financial advice.

That perspective is part of why the project emphasizes compact agent outputs, raw artifact preservation, deterministic downstream processing, explicit deployment tradeoffs, and conservative trust-boundary language instead of treating portfolio analysis as just another lightweight prompt wrapper.

## Requirements

- Python 3.9+
- OpenClaw >= 2026.0.0
- API keys (all optional, all have free tiers):
  - [Finnhub](https://finnhub.io/register) — real-time quotes and analyst ratings
  - [NewsAPI](https://newsapi.org/register) — portfolio news correlation
  - [Polygon.io](https://polygon.io/dashboard/signup) — analyst recommendations
  - [Alpha Vantage](https://www.alphavantage.co/support/#api-key) — supplemental price data
  - [FRED](https://fred.stlouisfed.org/docs/api/api_key.html) — Treasury benchmark yields

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

### Complexity note

InvestorClaw is substantially more complex than a typical lightweight ClawHub skill. It combines:

- portfolio file discovery and normalization
- multi-step analysis pipelines
- compact-vs-full artifact generation
- installer and setup flows
- guardrail enforcement and disclaimer wrapping
- optional local consultative LLM orchestration
- report persistence and downstream file workflows

That complexity is intentional, but it means installation, testing, and release expectations should be closer to a small application than to a trivial agent tool plugin.

At the same time, the skill was deliberately shaped around **context preservation** and **operational cost control**: compact stdout outputs keep agent context pressure lower than full raw report emission; full artifacts are written to disk for downstream use; the optional consultation layer can offload synthesis locally before the cloud operational model sees only reduced summaries.

Although development and validation were done on relatively powerful systems, InvestorClaw is intended to remain usable on a **modest single-system OpenClaw deployment** as well — a Mac running OpenClaw locally, or a Linux workstation with a local GPU in roughly the 16 GB VRAM class for consultation and enrichment workloads.

## Installation

> **ClawHub marketplace listing is in progress.** Until then, install directly from GitHub using the steps below.

### Installing from GitHub (current method)

```bash
# 1. Clone the repository to a stable local path
git clone https://github.com/perlowja/InvestorClaw.git ~/Projects/InvestorClaw

# 2. Install Python dependencies
pip install -r ~/Projects/InvestorClaw/requirements.txt

# 3. Register the plugin with OpenClaw
openclaw plugins install --link ~/Projects/InvestorClaw

# 4. Configure API keys
cp ~/Projects/InvestorClaw/.env.example ~/Projects/InvestorClaw/.env
# Edit .env — add at minimum FINNHUB_KEY for market data

# 5. Run first-time setup
python3 ~/Projects/InvestorClaw/investorclaw.py setup

# 6. Restart the OpenClaw gateway to load the plugin
openclaw gateway restart
```

Verify the plugin loaded after restart:
```bash
openclaw plugins inspect investorclaw
```

Run the smoke test to confirm the skill is fully operational:
```bash
python3 ~/Projects/InvestorClaw/tests_smoke.py
```

### Developer / contributor install

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

Guided setup and first-run helpers live under `setup/` and are invoked through the entry point. API key configuration is managed through `.env` (copied from `.env.example`) and optionally through the OpenClaw plugin config schema (`INVESTOR_CLAW_REPORTS_DIR`, `INVESTOR_CLAW_PORTFOLIO_DIR`, and provider key overrides).

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

## Who this is for

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

## Minimal getting-started path

If you want the simplest useful path:

1. install InvestorClaw
2. place your portfolio files in `~/portfolios`
3. configure one operational model in OpenClaw
4. run `python3 investorclaw.py setup`
5. run `python3 investorclaw.py holdings`
6. review `~/portfolio_reports/holdings.json`

You do **not** need the local consultation layer on day one. It is recommended, but not mandatory for basic operation.

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
| `update-identity` | `update_identity`, `identity` | — |
| `run` | `pipeline` | pipeline stdout + artifacts |
| `ollama-setup` | `model-setup`, `consult-setup` | stdout |
| `setup` | `auto-setup`, `init`, `initialize` | setup output |

Output files are written to `$INVESTOR_CLAW_REPORTS_DIR` (default: `~/portfolio_reports/`).

Add `--verbose` to any command for full detail (default is compact/summary output).

## Output Model

InvestorClaw follows a dual-output pattern:

| Output | What it contains | Audience |
|--------|------------------|----------|
| `stdout` | Compact, token-aware JSON or human-readable command output | OpenClaw agent context |
| Disk artifact | Full JSON, CSV, or Excel output | Human review and downstream tools |

The agent reads stdout exclusively. Each compact payload includes a `_note` key pointing to the full artifact path. This keeps sessions well within the context window of any 128K+ model.

Full artifact names: `holdings.json`, `performance.json`, `bond_analysis.json`, `analyst_data.json`, `portfolio_news.json`, `portfolio_analysis.json`, `fixed_income_analysis.json`, `session_profile.json`.

## Choosing Your Operational LLM

InvestorClaw uses a single operational LLM for routing, analysis, and guardrail enforcement through OpenClaw. In practice, the best model depends on whether you also run a local consultation model.

### Profile 1 — recommended hybrid architecture

**Operational LLM**: xAI Grok 4.1 Fast  
Model ID: `xai/grok-4-1-fast` (alias: `grok-reasoning`)

**Consultative LLM**: `gemma4-consult` on local Ollama

This is the recommended default architecture for most serious InvestorClaw users because it gives the best balance of:
- persistent-session context headroom (~2M tokens)
- operational cost control
- strong agentic responsiveness
- local deterministic synthesis before cloud interpretation

Why this is the default recommendation:
- Grok handles long-lived, tool-heavy OpenClaw sessions well
- the local consultative model reduces cloud token pressure
- raw portfolio detail can remain local while the operational model sees only reduced artifacts
- this split matches the architecture InvestorClaw was explicitly designed around

> **Compliance note**: `xai/grok-4-1-fast` requires running `/portfolio update-identity` at the start of each session. Without this step, guardrail disclaimer compliance drops to near zero. This is an xAI quirk, not an InvestorClaw bug.
>
> Config note: `xai/grok-4-1-fast-reasoning` and `grok-reasoning` are aliases for the same model. `xai/grok-4` (250K context) is a separate, smaller model — do not confuse them.

### Profile 2 — cloud-only premium / frontier deployment

If you do **not** have a local consultation model, the operational LLM must do more of the synthesis work directly. In that case, use stronger frontier models and treat them as session-specific InvestorClaw models rather than always-on defaults for all OpenClaw activity.

Recommended cloud-only frontier choices:

- **xAI Grok 4.1 Fast** — `xai/grok-4-1-fast` (~2M context) — still the primary recommendation even without local consultation
- **Google Gemini 3 Flash** — `google/gemini-3-flash-preview` (~1M context) — best high-context alternative
- **Together AI / Llama 4 Maverick** — `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` (~1M context) — good cost/context ratio
- **OpenAI GPT-5.4** — `openai/gpt-5.4` (266K context) — strong reasoning; verify your full session fits
- **OpenAI GPT-4.1** — `openai/gpt-4.1` (~1M context) — solid; multimodal

Important cost guidance:
- frontier models are often reasonable for **specific InvestorClaw sessions**
- they are usually **too expensive to leave as the primary always-on operational model** for constant use
- a good pattern is to keep a cheaper general OpenClaw default, then switch to a stronger frontier model only for high-value InvestorClaw workflows

> ⚠️ **Do not use GPT-4.1-nano** (`openai/gpt-4.1-nano`). Its Tier 1 rate limit is **30K TPM shared across all OpenClaw session activity**. Any concurrent agentic work exhausts the budget before a full portfolio analysis completes. Do not use it for InvestorClaw regardless of cost appeal.

### Profile 3 — modest single-system deployment

For a modest single-machine OpenClaw setup, InvestorClaw can still be useful without the full Developer Workstation / Inference Host reference environment.

Recommended practical approach:
- start with **xAI Grok 4.1 Fast** as the operational model
- add `gemma4-consult` later if/when a local inference path is available
- use premium frontier models selectively for demanding InvestorClaw sessions rather than for all OpenClaw traffic

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
| `xai/grok-4-1-fast` ⭐ | ~2M | xAI | **Primary recommendation**; needs `update-identity` each session |
| `google/gemini-3-flash-preview` | ~1M | Google | Best high-context alternative |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | ~1M | Together AI | Good cost/context ratio |
| `openai/gpt-4.1` | ~1M | OpenAI | Solid; multimodal |
| `openai/gpt-5.4` | 266K | OpenAI | Strong reasoning; verify session fits |
| `openai/gpt-5.3-chat-latest` | 391K | OpenAI | Newer; verify session fits |
| `nvidia/nemotron-3-super-120b-a12b` | 256K | NVIDIA NIM | On-premise / air-gapped |
| `groq/llama-3.3-70b-versatile` | 128K | Groq | Fast inference; small portfolios only |
| `openai/gpt-4.1-nano` | ~1M | OpenAI | ❌ **Not recommended** — 30K TPM Tier 1 limit |

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

**Hardware requirements**: 12+ GB VRAM, CUDA compute capability ≥ 8.0 (RTX 30xx / A-series / Ada Lovelace or newer), Ollama ≥ 0.20.x.

Other tested models: `gemma4:e4b`, `nemotron-3-nano`, `qwen2.5:14b`. Run `/portfolio ollama-setup` to auto-detect available models on your Ollama endpoint.

## Configuration examples

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
        "primary": "google/gemini-3-flash-preview"
      }
    }
  }
}
```

Or:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai/gpt-4.1"
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

## Data locality and privacy model

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

## Limitations and non-goals

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

## Authority model: operational vs consultative output

When consultation is enabled, InvestorClaw deliberately separates **operational orchestration** from **consultative synthesis**.

**When consultation is enabled**: the operational LLM is expected to **quote, relay, or frame** the consultative result rather than invent a fresh competing portfolio judgment. The operational model behaves as the messenger and orchestrator, not as a second independent portfolio analyst rewriting the result from scratch.

**When consultation is not enabled**: the operational LLM does more direct synthesis work itself; stronger frontier cloud models become more attractive for demanding sessions because there is no local synthesis layer narrowing the task.

**Why this split exists**: to improve determinism, preserve context budget, keep raw artifacts out of repeated conversational turns, and reduce the chance that two different LLM stages make competing observations about the same portfolio state.

## Example end-to-end workflow

1. Put portfolio files in `~/portfolios`
2. Run setup / discovery to normalize the inputs
3. Generate holdings, performance, bond, analyst, and news outputs
4. Full artifacts written to `~/portfolio_reports/.raw/`
5. Compact summaries emitted to stdout and agent-readable summary files
6. If consultation is enabled, synthesize locally before the operational model frames the result
7. Use lookup extraction later when a follow-up question needs a specific symbol or detail

This workflow is the core of InvestorClaw's design: raw artifacts on disk preserve completeness; compact artifacts in chat preserve context budget; lookup extraction preserves precision without reloading everything; consultation-first synthesis preserves more disciplined model behavior when the optional local layer is enabled.

## FINOS CDM scope

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

## Security

InvestorClaw implements several security measures:

- **PII scrubbing**: credit card numbers, SSNs, and account IDs are redacted from CSV columns before processing
- **Prompt injection defense**: portfolio text columns are scanned for injection patterns before data is passed to the LLM
- **Math verification**: all financial calculations are performed by deterministic Python scripts — the LLM never computes portfolio math in-context
- **Data locality**: raw CSV data is never sent to external APIs; only computed summaries are passed to the cloud LLM
- **Guardrails**: `data/guardrails.yaml` enforces educational-only output, blocks suitability assessments, and prevents specific investment recommendations

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
python3 tests_smoke.py
```

## Compliance

**NOT INVESTMENT ADVICE.** InvestorClaw provides educational portfolio analysis only. It is not a substitute for professional financial advice and does not assess personal risk tolerance, goals, or investment suitability.

## License

MIT — see [LICENSE](LICENSE).
