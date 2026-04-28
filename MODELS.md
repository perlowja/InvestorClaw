# InvestorClaw — Tested Models and Benchmark Results

**Harness: V8.1** (current) | **Context**: V7.1 (historical for reference) | **Last updated**: 2026-04-16

---

## V8.1 Test Harness: Google & xAI Focus (IC-RUN-20260416-UNIFIED)

**Platform**: mac-dev-host (OpenClaw 2026.4.15-beta.1) | **API Key Config**: K2 (full) | **Test Scope**: W0–W8 (39 checkpoints)

### Test Matrix — Google Gemini + Together AI + xAI

Six canonical model combinations across **cloud-only** and **hybrid** deployment modes:

#### Together AI Models (M1, HB1 — Best Price/Performance)

| Model | Mode | Cloud QC4 | Hybrid QC4 | Cost/mo (1M tokens) | Notes |
|---|---|:---:|:---:|:---:|---|
| `together/MiniMaxAI/MiniMax-M2.7` | Cloud + Hybrid | 108 (WF82) | 97 (WF87) | $0.30 | **#1 single-model overall.** Cloud-only recommended (consultation hurts). Best price/performance. |
| `together/zai-org/GLM-5` | Cloud + Hybrid | 74 (WF83) | 86 (WF90) | $1.00 | **Best hybrid under current stack.** +16% under consultation. Rich account breakdown. |

**Key V8.1 finding**: Together AI models are production-ready; best value-to-quality ratio.

---

#### Google Models (M2, M3, HB2, HB3 — Enterprise Scale)

| Designation | Model | Mode | Consultation | W0 | W1–W8 | Stonkmode | QC4 |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| **M2** | `google/gemini-3-flash-preview` | Cloud-only | None | ✅ | ✅ | ✅ | — |
| **M3** | `google/gemini-3.1-pro-preview` | Cloud-only | None | ✅ | ✅ | ✅ | 46 (WF80) |
| **HB2** | `google/gemini-3-flash-preview` + local | Hybrid | GPU host :8080 | ✅ | ✅ | ✅ | — |
| **HB3** | `google/gemini-3.1-pro-preview` + local | Hybrid | GPU host :8080 | ✅ | ✅ | ✅ | 38 (WF91) |

**Google models status**: Fully functional across all W0–W8 commands. **Gemini-3.1-pro is the recommended enterprise model** — 1M context window, QC4=46 cloud-only, shows 2.7× improvement under context injection (WF65: 17→WF80: 46). Cloud-only recommended; hybrid mode (HB3) regresses to QC4=38 (consultation neutral/harmful).


---

## Mode Definitions

Understanding the distinction between these two modes is essential for reading the tables below.

### Hybrid mode (operational + consultation)

The operational LLM routes the session, runs tools, and frames the synthesis output. A separate **local consultation model** (`gemma4-consult` via a local Ollama endpoint) runs before synthesis and enriches each portfolio symbol with a structured analyst summary. The operational model receives compact enriched records, not raw data.

- Requires a local GPU host running Ollama with `gemma4-consult` (or a compatible model)
- Produces HMAC-fingerprinted synthesis records with `verbatim_required=true` and `is_heuristic=false`
- Enables the anti-fabrication controls: fingerprint chain, verbatim attribution, quote artifact
- **The local enrichment layer, not the operational model, is the primary driver of information density**

### Single-model mode (operational only, no consultation)

The operational LLM handles all routing, tool calls, and synthesis directly from heuristic analyst summaries. No local enrichment step. No fingerprint controls.

- Works with any capable cloud operational LLM
- No GPU or local inference required
- Lower information density on portfolios with many individual equities
- Still enforces guardrails and educational-only output

---

## Recommended Configurations

Choose based on your priorities:

| Priority | Config | Mode | Model | Rationale |
|----------|--------|------|-------|-----------|
| **#1 Best overall (no GPU)** | RC-1 | Cloud-only | `together/MiniMaxAI/MiniMax-M2.7` | QC4=108; $0.30/$1.20/M. No GPU needed. Consultation hurts (→QC4=97). Recommended for ≤500 holdings. |
| **#2 Best with GPU (audit controls)** | RC-2 | Hybrid | `together/zai-org/GLM-5` + `gemma4-consult` | QC4=86; gains +16% from consultation. Enables HMAC fingerprint chain. Best hybrid for cost. |
| **#3 Enterprise (1M context, 200+ holdings)** | RC-3 | Cloud-only | `google/gemini-3.1-pro-preview` | QC4=46; 1M context window; excellent synthesis; ethically sourced. Cloud-only (consultation regresses to QC4=38). |
| **#4 Speed-optimized (low density acceptable)** | RC-4 | Cloud-only | `groq/openai/gpt-oss-120b` | QC4=17; $0.15/$0.60/M; ~500 tok/s. Fast but lower synthesis density. For cost-sensitive use. |

---

## Benchmark Scores — V8.1 (Production Validation)

V8.1 comprehensive testing validates all 4 recommended configurations with real portfolio data (215 holdings, mixed equities/bonds/ETFs). All W0–W8 commands pass exit_code=0. Scores measured on W6 synthesis output — the highest-value single response in a typical InvestorClaw session.

### Hybrid Mode (with local consultation)

| Rank | Configuration | QC4 | Notes |
|------|--------------|:---:|-------|
| 🥇 | `together/MiniMaxAI/MiniMax-M2.7` + `gemma4-consult` | **97** | **Recommended for audit controls.** Highest hybrid QC4. HMAC fingerprint chain + `is_heuristic=false`. Cloud-only (QC4=108) is higher; use hybrid only for fabrication detection. |
| 🥈 | `together/zai-org/GLM-5` + `gemma4-consult` | **86** | Best where consultation adds value (+16% vs cloud-only). Excellent account-level breakdown. |
| 🥉 | `together/moonshotai/Kimi-K2.5` + `gemma4-consult` | **82** | +49% vs cloud-only. Rich narrative, full bond analytics. |
| | `google/gemini-3.1-pro-preview` + `gemma4-consult` | **38** | Regresses 17% under consultation. Use cloud-only instead. |
| ⚠️ | `groq/openai/gpt-oss-120b` + `gemma4-consult` | **8** | Severe regression (−53%). **Do not use hybrid.** |

### Cloud-Only Mode (recommended for most users)

| Rank | Model | QC4 | Notes |
|------|-------|:---:|-------|
| 🥇 | `together/MiniMaxAI/MiniMax-M2.7` | **108** | **Top single-model overall.** Best price-to-quality ratio ($0.011/QC4-point). Default recommendation. |
| 🥈 | `together/zai-org/GLM-5` | **74** | Excellent context utilization; structured tables. |
| 🥉 | `together/moonshotai/Kimi-K2.5` | **55** | Strong narrative quality. 262K context for large portfolios. |
| | `google/gemini-3.1-pro-preview` | **46** | Enterprise choice (1M context, ethically sourced). Cloud-only viable. |
| | `together/deepseek-ai/DeepSeek-V3.1` | **44** | Solid all-around performer. $0.60/$1.70/M. |
| | `openai/gpt-5.4` | **28** | Mid-tier fallback. Smallest context (272K). |
| | `groq/openai/gpt-oss-120b` | **17** | Budget speed option (~500 tok/s). Low synthesis density. |

**Key finding**: Consultation does NOT uniformly improve synthesis. Beneficial: Kimi-K2.5 (+49%), GLM-5 (+16%). Harmful: MiniMax-M2.7 (−10%), Gemini (−17%), GPT-OSS-120b (−53%). Use hybrid mode only when HMAC fingerprint controls are required, not for synthesis improvement.

### Guardrail Compliance

All PASS models: **QC8=0 fabrication** across all test commands. Production-ready for educational-only deployments with no false financial recommendations.

---

## Context Window Comparison

Context window capacity is a separate model selection axis from synthesis quality (QC4). For the current 215-holding portfolio in compact mode, context is not the bottleneck — models are using 17–34K tokens, well within every supported model's limit. Context becomes the decisive dimension as portfolio size, session length, or enrichment depth increases.

### Context tiers

| Tier | Models | Context | When this tier matters |
|------|--------|--------:|------------------------|
| **Tier 1: 2M** | `xai/grok-4-1-fast` | ~2,000K | Only model in this tier. 8–15× capacity advantage over all others. Comfortable for any non-compact, enterprise-scale, or extended-session scenario. |
| **Tier 2: ~1M** | `xai/grok-4.20-0309-non-reasoning`, `google/gemini-3.1-pro-preview` | ~977K–1M | Ample for non-compact mode; handles large portfolios and multi-turn accumulation. |
| **Tier 3: 262–272K** | `openai/gpt-5.4`, `together/moonshotai/Kimi-K2.5`, `groq/moonshotai/kimi-k2-instruct-0905` | 262–272K | Adequate for large compact-mode sessions; tight under non-compact with full enrichment. |
| **Tier 4: 197–203K** | `together/MiniMaxAI/MiniMax-M2.7`, `together/zai-org/GLM-5` | 197–203K | Fine for typical compact sessions; not recommended for non-compact with >150 enriched symbols. |
| **Tier 5: 128–131K** | `together/deepseek-ai/DeepSeek-V3.1`, `groq/openai/gpt-oss-120b`, `groq/openai/gpt-oss-20b` | 128–131K | Smallest working tier. Sufficient for the 215-holding compact benchmark; marginal for enriched or extended sessions. |

### Portfolio token utilization (reference)

| Scenario | Estimated tokens | Fits in tier 3+? | Fits in tier 4+? | Fits in tier 5? |
|----------|----------------:|:----------------:|:----------------:|:---------------:|
| 215 holdings, compact mode (benchmark) | ~17–34K | ✅ | ✅ | ✅ |
| W1 raw output alone, non-compact | ~72K | ✅ | ✅ | ✅ |
| Full enriched session (215 symbols) | ~80–120K | ✅ | ✅ | ⚠️ tight |
| Large portfolio, non-compact (500 holdings) | ~300–400K | ✅ | ❌ | ❌ |
| Enterprise portfolio + long session (1000+ holdings) | ~1M+ | ✅ (Gemini) | ❌ | ❌ |

### Takeaway: where grok-4-1-fast fits on context

`xai/grok-4-1-fast` is the **only model in the 2M tier** — a unique capacity advantage that no current Together AI, Groq, or OpenAI option comes close to. For the standard 215-holding compact-mode benchmark, this advantage is invisible (all models have headroom). It becomes the decisive factor when:

- Running non-compact mode at scale (raw W-step data exhausts smaller-context models)
- Scaling to enterprise-size portfolios (500–1000+ positions)
- Multi-turn sessions where accumulated history approaches model limits
- Maximizing enrichment density without context truncation risk

grok-4-1-fast is the **Profile 4 LLM — use it when context capacity is the binding constraint**, not as a general operational default. For standard portfolios (≤200 holdings non-compact, ≤500 compact), MiniMax-M2.7 (Profile 1/2) delivers higher synthesis density at lower cost. When portfolios scale beyond those thresholds, grok-4-1-fast's 2M context window becomes the decisive factor regardless of synthesis score. Consultation is required: hybrid QC4=52 (WF88, +33% vs cloud-only QC4=39 WF85).

---

## Provider Model Catalog

**Due Diligence Reference**: The catalog below documents all tested models for transparency. The [Recommended Configurations](#recommended-configurations) section above contains the production-ready defaults. Providers are ranked by production readiness and cost-effectiveness; special-use models (high-context scenarios, experimental) appear at the end.

---

### Together AI (Primary Recommendation — Best Price/Quality)

| Model | Context | Benchmark | Notes |
|-------|---------|:---------:|-------|
| `together/moonshotai/Kimi-K2.5` | 262K | ✅ WF60/WF66/WF76 (single) / ✅ WF71/WF84 (hybrid) | Single WF76: QC3=16, QC4=55, QC5=256. Hybrid WF84: QC3=24, QC4=82, QC5=579 — **#3 hybrid overall** (WF87–WF94 stack); 4.6× over WF71. 262K context fits large compact-mode sessions. W7 questionnaire loop in both modes. |
| `together/deepseek-ai/DeepSeek-V3.1` | 131K | ✅ WF68/WF75 | PASS — re-benchmarked WF75: QC3=13, QC4=44, QC5=160. $0.60/$1.70/M. |
| `together/MiniMaxAI/MiniMax-M2.7` | 197K | ✅ WF69/WF82 | PASS — re-benchmarked WF82: QC3=27, QC4=108, QC5=541. **#1 single-model overall** with context injection. $0.30/$1.20/M — best value of all top performers. |
| `together/zai-org/GLM-5` | 203K | ✅ WF70/WF83 | PASS — re-benchmarked WF83: QC3=20, QC4=74, QC5=481. Excellent context utilization; rich account breakdown. $1.00/$3.20/M. |
| `together/Qwen/Qwen3-235B-A22B-Instruct-2507-tput` | 262K | ✅ WF61 (single) | ~300-word synthesis; 60k/262k context use. |
| `together/MiniMaxAI/MiniMax-M2.5` | — | ⚠️ DEGRADED | `/portfolio synthesize` not recognized; W5 news non-functional — use M2.7 instead. |
| `together/Qwen/Qwen3-235B-A22B-Thinking-2507` | — | ⚠️ PARTIAL | Tool calls work; 5–10 min/step — not viable for interactive sessions. |
| `together/deepseek-ai/DeepSeek-R1-0528` | — | 🚫 BLOCKED | Outputs tool name as text code block, not a function call. |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | — | 🚫 BLOCKED | Tool payload rejected by Together AI serverless. |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct` | — | 🚫 BLOCKED | Tool payload rejected (Together AI variant). |
| `together/moonshotai/Kimi-K2-Thinking` | — | 🚫 BLOCKED | Thinking variant not tool-call compatible. |
| `together/zai-org/GLM-4.7` | — | 🚫 BLOCKED | GLM-5 works; GLM-4.7 does not. |
| `together/Qwen/Qwen3-Next-80B-A3B-Instruct` | — | 🚫 BLOCKED | MoE 80B variant not tool-call compatible. |

### Google (Enterprise Scale — 1M Context)

| Model | Context | Benchmark | Notes |
|-------|---------|:---------:|-------|
| `google/gemini-3.1-pro-preview` | ~1M | ✅ WF65/WF80 | **Recommended for enterprise (>200 holdings).** Re-benchmarked WF80: QC3=15, QC4=46, QC5=340. Significant improvement from context injection (WF65: QC4=17→WF80: QC4=46). 1M context; cloud-only viable (hybrid regresses to QC4=38). Ethically sourced; no training data concerns. |

### OpenAI (Mid-Tier Fallback)

| Model | Context | Benchmark | Notes |
|-------|---------|:---------:|-------|
| `openai/gpt-5.4` | ~272K | ✅ WF63/WF81 | PASS — re-benchmarked WF81: QC3=14, QC4=28, QC5=178. Mid-tier synthesis (QC4=28). 272K context is smallest among frontier models. W7 questionnaire loop. |

### Groq (Speed-Optimized Budget Tier)

Fast inference (500–1000 tok/s) at ultra-low cost ($0.075–0.15/M tokens). 128K context limits to small-to-medium portfolios — not suitable for large multi-account or fully-enriched sessions.

| Model | Context | Benchmark | Notes |
|-------|---------|:---------:|-------|
| `groq/openai/gpt-oss-120b` | 128K | ✅ WF46/WF78 | **Recommended Groq option.** Re-benchmarked WF78: QC3=19, QC4=17, QC5=376 — verbose but low metric density. $0.15/$0.60/M; 500 tok/s. Production-stable. |
| `groq/openai/gpt-oss-20b` | 128K | ✅ WF59 / 🚫 WF79 | WF79 FAIL: malformed tool call `read<|channel|>commentary`. Previously functional (WF59). Current endpoint behavior incompatible — do not use. $0.075/$0.30/M. |
| `groq/moonshotai/kimi-k2-instruct-0905` | 262K | ✅ WF58/WF77 ⚠️ | Re-benchmarked WF77: QC3=9, QC4=25, QC5=151. **Preview tier — not production-stable; may be discontinued without notice.** |
| `groq/qwen/qwen3-32b` | 128K | ⚠️ WF67 DEGRADED | `/portfolio update-identity` not recognized; W6 thin synthesis (~60 words) with file pointer; W7 offered specific investment recommendations without educational framing (guardrail issue). Preview model. |
| `groq/meta-llama/llama-4-scout-17b-16e-instruct` | 128K | ⚠️ DEGRADED | Requires extra prompt step for W6 prose; heat_level type error; preview model. |
| `groq/moonshotai/kimi-k2-instruct` | 128K | ⚠️ DEGRADED | Thin synthesis (~144 words); undocumented endpoint. |
| `groq/llama-3.3-70b-versatile` | 128K | 🚫 DO NOT USE | Config corruption risk — wrote unauthorized keys into `openclaw.json` during testing. |

> **Groq stability note**: Production-stable models confirmed in official Groq docs: `llama-3.1-8b-instant`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`. Preview/beta models (`qwen3-32b`, `llama-4-scout`, `kimi-k2-instruct-0905`) can be discontinued without notice.

### xAI (Grok) — Due Diligence: High-Context Scenarios Only

| Model | Context | Benchmark | Notes |
|-------|---------|:---------:|-------|
| `xai/grok-4-1-fast` | ~2M | ✅ WF39/WF62/WF72/WF85/WF88 | **Special use only: high-context / enterprise scale.** The only model in the 2M context tier — use ONLY when portfolio exceeds ~500 holdings (compact) or non-compact mode risk context truncation. Synthesis quality (QC4=39 cloud, 52 hybrid) is mid-tier; use MiniMax-M2.7 or GLM-5 for standard portfolios. **Context capacity is the selection reason, not synthesis quality.** |
| `xai/grok-4.20-0309-non-reasoning` | ~1M | ⚠️ WF74 PASS (hybrid only) / 🚫 WF86 FAIL (cloud-only) | **Hybrid-only, not recommended.** Cloud-only consistently fails with tool payload rejection (WF64, WF86). Hybrid-only (WF74): QC3=14, QC4=17. Use Google Gemini-3.1-pro instead (1M context, QC4=46, cloud-only viable). |

---

## Together AI Tool-Call Compatibility

Not all Together AI serverless models support OpenAI function-calling schema. InvestorClaw requires tool execution — models that reject tool payloads cannot complete the workflow.

| Works (tool-call compatible) | Blocked (rejects tool payload) | Incompatible (text output only) |
|------------------------------|-------------------------------|----------------------------------|
| DeepSeek-V3.1 | Llama-4-Maverick FP8 | DeepSeek-R1-0528 (tool name as code block) |
| MiniMax-M2.5 / M2.7 | Llama-4-Scout | — |
| GLM-5 | GLM-4.7 | — |
| Kimi-K2.5 | Qwen3-Next-80B | — |
| Qwen3-235B-Instruct-tput | Kimi-K2-Thinking | — |
| Qwen3-235B-Thinking* | — | — |

*Qwen3-235B-Thinking makes tool calls correctly but takes 5–10 min per response step — not viable for interactive harness runs.

---

## Anti-Fabrication Properties (Hybrid Mode Only)

The tier-3 enrichment path adds audit controls that no single-model configuration provides:

- **HMAC fingerprint chain** — each enriched record gets a 16-character hex fingerprint; the session accumulates a chained fingerprint across all enriched symbols for post-hoc verification
- **`verbatim_required=true` + attribution** — enriched analyst quotes carry a verbatim flag and source attribution; the synthesis layer is constrained to cite rather than paraphrase
- **`is_heuristic=false`** — signals that synthesis was produced from enriched model inference, not keyword matching
- **`synthesis_instruction`** — machine-readable citation directive injected into the compact analyst payload; tells the operational LLM to cite synthesis verbatim with fingerprint included

These controls are absent in all single-model configurations regardless of model capability.

---

## Consultation Model Catalog (Local Ollama)

Tested on the inference host (RTX 4500 Ada 24 GB VRAM, Ollama 0.20.3).

| Model | tok/s | VRAM | Notes |
|-------|------:|-----:|-------|
| `gemma4-consult` | ~65 | 9.6 GB | **Recommended** — tuned gemma4:e4b; optimized for consultative Q&A (num_ctx=4096, num_predict=1200, up to 400 words per symbol) |
| `gemma4:e4b` | ~66 | 9.6 GB | Base model; good quality/speed tradeoff; 128K context |
| `gemma4:e2b` | ~99 | 7.2 GB | Fastest; suitable for lighter tasks |
| `nemotron-3-nano:30b-a3b-q4_K_M` | ~25 | 24 GB | High-quality fallback; requires full VRAM |
| `qwen2.5:14b-instruct-q4_K_M` | ~45 | 9.0 GB | Code and structured output |

Create `gemma4-consult`:
```bash
ollama create gemma4-consult -f docs/gemma4-consult.Modelfile
```

Run `/portfolio ollama-setup` to auto-detect available models on your endpoint.

---

## Reproducibility

The full test harness is at `docs/harness-v71.txt` in the repository root.

```bash
# Prerequisites
# - OpenClaw gateway running with investorclaw plugin loaded
# - (Optional) local Ollama host at INVESTORCLAW_CONSULTATION_ENDPOINT
# - Portfolio CSVs in INVESTOR_CLAW_PORTFOLIO_DIR
# - .env copied to workspace: cp ~/Projects/InvestorClaw/.env ~/.openclaw/workspace/skills/investorclaw/.env

# Covers 39 workflow checkpoints across 5 phases (W0–W8)
```

### Critical: consultation is controlled by the project .env, not the workspace .env

InvestorClaw loads from the registered plugin path (`~/Projects/InvestorClaw/dist/index.js`, origin: "config"), not from the OpenClaw workspace skill directory. This means:

- **`~/Projects/InvestorClaw/.env`** is the authoritative consultation config — changes here take effect after gateway restart.
- **`~/.openclaw/workspace/skills/investorclaw/.env`** affects only the background enricher subprocess when it does NOT inherit the parent process environment. Setting `INVESTORCLAW_CONSULTATION_ENABLED=false` in the workspace `.env` has **no effect** on the plugin loaded from the project directory.

To disable consultation for a clean single-model benchmark run:
```bash
# Edit ~/Projects/InvestorClaw/.env
INVESTORCLAW_CONSULTATION_ENABLED=false
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:0   # unreachable — belt-and-suspenders
```

No gateway restart required — the OpenClaw gateway hot-reloads `openclaw.json` model config changes. For clean runs, **delete the session** rather than restarting the gateway:

```python
# Delete the session from ~/.openclaw/sessions/sessions.json before each run
import json
from pathlib import Path
store = Path.home() / ".openclaw/sessions/sessions.json"
data = json.loads(store.read_text())
data.pop("agent:main:explicit:<session-id>", None)
store.write_text(json.dumps(data, indent=2))
```

Then run with a fresh session ID — the hot-reloaded model config takes effect immediately. The IC-RUN-20260414-003 batch (WF75–WF84) used this approach: no gateway restarts across 10 sequential runs.

---

## Cross-Platform Battery (2026-04-14, MiniMax-M2.7)

Both platforms ran the full T1–T8 battery in a shared session context with `together/MiniMaxAI/MiniMax-M2.7`.

| Test | Apple Silicon (mac-dev-host) | Raspberry Pi 4 (pi-large) | Verdict |
|------|------------------------|-------------------------|---------|
| T1 Smoke | FAIL — script bug¹ | FAIL — script bug¹ | Both |
| T2 Portfolio Load | 47,837 tok ✅ | 206s ✅ | Pass |
| T3 Bonds | 48,754 tok ✅ | 58s ✅ | Pass |
| T4 Performance | 70,094 tok ✅ | 196s ✅ | Pass |
| T5 Analyst | 75,418 tok ✅ | 152s ✅ | Pass |
| T6 News | 77,712 tok ✅ | 32s ✅ | Pass |
| T7 Synthesize | 79,230 tok ✅ | 34s ✅ | Pass |
| T8 Guardrails | 79,557 tok ✅ | 23s ✅ | Pass |

**Functional parity confirmed.** Portfolio value, bond analytics (99.6% muni concentration, YTM/duration), analyst flags, and synthesis output were identical on both platforms.

**Pi timing note**: T2 and T4 are slow (3+ min) due to heavy Python data processing (pandas/polars over 270 positions). T6–T8 are fast (23–34s) because they operate on cached session context.

¹ T1 smoke test bug: uses relative `venv/bin/python` path (fails when cwd ≠ skill dir) and `date +%s%3N` which is GNU-only. Fix: use `$SKILL_DIR/venv/bin/python` and `python3 -c "import time; print(int(time.time()*1000))"`.

**Pi gateway note**: restart the gateway before running a battery (`openclaw gateway restart`). A stuck gateway causes 210s timeout before falling back to embedded mode.

This finding (DEV-003, discovered IC-RUN-20260413-010) invalidated the 9 earlier Phase 5 benchmark runs (WF36–WF41, WF48, WF53–WF55) that had attempted to disable consultation via workspace `.env` modifications. All 9 were re-run cleanly in WF63–WF71.
