# InvestorClaw Dual-Model Architecture

**Updated**: 2026-04-16  
**Status**: ✅ COMPLETE  
**Models**: Gemma (Consultation) + MiniMax (Narrative)

---

## Architecture Overview

InvestorClaw uses a **dual-model strategy** that separates computational work from presentation quality:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Command                              │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────────────────┬─────────────────────────┐
             │                         │                         │
             ▼                         ▼                         ▼
       ┌──────────────┐          ┌──────────────┐         ┌──────────────┐
       │ Analysis     │          │ Synthesis    │         │ Lookup       │
       │ (Determinism│          │ (Gemma 4)    │         │ (Determinism)│
       │ Python)     │          │ Hard Worker  │         │              │
       └──────┬───────┘          └──────┬───────┘         └──────┬───────┘
              │                         │                        │
              └─────────────┬───────────┴────────────┬───────────┘
                            │                        │
                            ▼                        ▼
                    ┌──────────────────────────────────────────┐
                    │  MiniMax Presentation Layer              │
                    │  - Narrative synthesis                   │
                    │  - Stonkmode entertainment (optional)    │
                    │  - Gets full OpenClaw context            │
                    └──────────┬───────────────────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  User Output │
                        │ (Clean or    │
                        │  Entertaining)
                        └──────────────┘
```

---

## Model Responsibilities

### Gemma-4-31B (Hard Worker — Analysis)

**Purpose**: Computational analysis, synthesis, consultation  
**Characteristics**:
- Isolated from context injection (no complex prompting)
- Focused, deterministic tasks
- Handles portfolio analysis, risk assessment, adviser synthesis
- Runs via Together.ai cloud API

**Configuration**:
```env
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_MODEL=google/gemma-4-31B-it
INVESTORCLAW_CONSULTATION_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_CONSULTATION_API_KEY=<your-together-api-key>  # Set in .env, not in code
```

**Optional Local Override** (if 24GB+ GPU available):
```env
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
INVESTORCLAW_CONSULTATION_MODEL=gemma-4-31B-it
```

---

### MiniMax-M2.7 (Presentation Layer — Narrative)

**Purpose**: All narrative output (whether stonkmode on/off)  
**Characteristics**:
- Receives full OpenClaw context from agent
- Handles complex narrative synthesis
- Optimized for creative, engaging output
- Optional entertainment layer (stonkmode) on top
- Used for all synthesis presentation, not just stonkmode

**Configuration**:
```env
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=<your-together-api-key>  # Set in .env, not in code
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
```

---

## User Scenarios

### Scenario A: Cloud-Only (Default)
Best for: Users without local GPU

```env
# Gemma: Cloud
INVESTORCLAW_CONSULTATION_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_CONSULTATION_MODEL=google/gemma-4-31B-it

# MiniMax: Cloud
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
```

### Scenario B: Hybrid (GPU Optional)
Best for: Users with 24GB+ GPU who want local analysis

```env
# Gemma: Local
INVESTORCLAW_CONSULTATION_ENDPOINT=http://your-gpu-host:8080
INVESTORCLAW_CONSULTATION_MODEL=gemma-4-31B-it

# MiniMax: Cloud (presentation always benefits from context)
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
```

### Scenario C: Large Portfolios (200+ positions)
Best for: Large portfolios needing Grok's 200K context

```env
# Grok: Cloud (huge context for synthesis)
INVESTORCLAW_CONSULTATION_ENDPOINT=https://api.x.ai/v1
INVESTORCLAW_CONSULTATION_MODEL=grok-4-1-fast
INVESTORCLAW_CONSULTATION_API_KEY=<your-xai-api-key>  # Set in .env, not in code

# MiniMax: Cloud (presentation)
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
```

---

## Cost Analysis

### Per-Command Costs (Scenario A — Cloud-Only)

**Consultation** (optional, per synthesis command):
- Gemma-4: ~1700 tokens = **$0.002 per call**
- Frequency: ~4/month = **$0.008/month**

**Narrative** (all synthesis commands):
- MiniMax: ~800 tokens = **$0.001 per call**
- Stonkmode narration: 2 calls (lead + foil) = **$0.0002 per command**
- Frequency: ~10x/month = **$0.002/month**

**Total**: ~**$0.01/month** (negligible)

---

## Implementation Notes

### Backward Compatibility
The code supports both old and new variable names:
- Old: `INVESTORCLAW_STONKMODE_*` (maps to narrative layer)
- New: `INVESTORCLAW_NARRATIVE_*` (preferred for new configs)

Existing configs continue to work. New configs should use `INVESTORCLAW_NARRATIVE_*`.

### Why This Architecture?

1. **Separation of Concerns**: Computation (Gemma) vs. Presentation (MiniMax)
2. **Context Awareness**: Narrative layer gets full agent context; analysis stays isolated
3. **Cost Efficient**: Analysis is computational (optimize for cost), presentation is creative (optimize for quality)
4. **Scalable**: Supports cloud-only → hybrid → large-portfolio use cases
5. **Optional Features**: Stonkmode works independently; users without Gemma still get MiniMax narration

---

## Testing

All configurations tested with:
- ✅ Gemma-4-31B cloud synthesis
- ✅ MiniMax-M2.7 cloud narration
- ✅ Stonkmode entertainment layer (with MiniMax)
- ✅ Regular (non-stonkmode) narrative output

See: `STONKMODE_NARRATION_FIX_20260416.md` for fix details.

---

## Related Architecture Docs

- **[ARCHITECTURE_INDEX.md](ARCHITECTURE_INDEX.md)** — Navigation guide for all architecture docs
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Code module structure
- **[ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md)** — Design principles and rationale

---

## References

- **Models**: See `MODELS.md` for profile benchmarks
- **Configuration**: `.env` (environment variables)
- **Code**: `rendering/`, `internal/tier3_enrichment.py`
- **Setup**: `setup/setup_wizard.py` (Step 2 — local GPU detection)

---

**Last Updated**: April 2026  
**Maintainer**: @perlowja
