# Architecture Documentation

InvestorClaw is built on the principle that **the LLM synthesizes language; Python handles everything else**. This section explains the architecture from different perspectives.

---

## Quick Navigation

Choose the doc that matches your role:

| Role | Document | What You'll Learn |
|------|----------|-------------------|
| **Contributor** | [ARCHITECTURE.md](ARCHITECTURE.md) | How the code is organized; module structure; how to add commands |
| **Tech Lead** | [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) | Why we made key design choices; production principles; quality dimensions |
| **Operator/Deployer** | [ARCHITECTURE_MODELS.md](ARCHITECTURE_MODELS.md) | How we use Gemma + MiniMax; consultation tiers; deployment modes |

---

## Core Principles (All Architectures)

1. **Deterministic Computation First** — All financial math happens in Python before the LLM ever sees the data
2. **Provider Resilience** — Multi-tier fallback chain (primary → secondary → cache → synthetic)
3. **Context as a Resource** — Aggressive compression (72K tokens → <1K) for LLM input
4. **Guardrails as Rules** — Output validation enforces policies, not prompts
5. **Comprehensive Testing** — 442 unit tests, 114 workflow validations, 18 smoke tests

---

## Document Overview

### [ARCHITECTURE.md](ARCHITECTURE.md) — Code Organization
**Audience**: Developers, contributors

- Entry point (`investorclaw.py`) and command dispatch
- Module structure (`commands/`, `services/`, `providers/`, `rendering/`)
- Command registry and routing
- Configuration loading and path resolution
- Guardrail priming and consultation policy
- Testing infrastructure

**Use this if**: You're adding a new command, modifying routing logic, or understanding module dependencies.

---

### [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) — Design Philosophy
**Audience**: Tech leads, architects, reviewers

- Separation of concerns (LLM synthesis vs Python computation)
- Deterministic financial calculations
- Provider resilience through graceful degradation
- Context window management and compression
- Structured guardrails as rules engine
- Comprehensive testing framework
- Data governance and security
- Deployment modes (individual, advisory, institutional)
- Quality dimensions and future considerations

**Use this if**: You're evaluating the architecture, understanding design tradeoffs, or making decisions about new features.

---

### [ARCHITECTURE_MODELS.md](ARCHITECTURE_MODELS.md) — Dual-Model Strategy
**Audience**: Operators, deployment engineers, model selection

- Dual-model separation (Gemma-4 analysis + MiniMax narrative)
- Model responsibilities and context windows
- Consultation tiers (Tier 1, 2, 3)
- Deployment profiles and model recommendations
- Provider selection (Together.ai, Google Gemini, Groq, local Ollama)
- Performance and cost tradeoffs

**Use this if**: You're deploying InvestorClaw, choosing which models to use, or understanding the consultation pipeline.

---

## Related Docs

- **[SKILL.md](../SKILL.md)** — OpenClaw plugin specification
- **[CONFIGURATION.md](../CONFIGURATION.md)** — Environment variables and settings
- **[DEPLOYMENT.md](../DEPLOYMENT.md)** — Production runbook
- **[MODELS.md](../MODELS.md)** — Model benchmarks and recommendations
- **[STONKMODE.md](STONKMODE.md)** — Entertainment mode documentation

---

## Quick Reference: Key Design Decisions

| Decision | Rationale | Evidence |
|----------|-----------|----------|
| **Python-first computation** | LLMs unreliable for math; enables auditability | `services/portfolio_utils.py` |
| **Multi-provider fallback** | Single-point failures are unacceptable | `providers/price_provider.py` |
| **Context compression** | Token cost and latency bottleneck | `rendering/compact_serializers.py` |
| **Guardrails as rules** | Prompt instructions are best-effort | `config/guardrail_enforcer.py` |
| **Dual-model split** | Analysis precision + narrative quality | `ARCHITECTURE_MODELS.md` |
| **Extensive testing** | Financial software demands high coverage | 442 unit tests in `tests/` |

---

## Architecture Diagram

```
User Command
    │
    ├─── Python Computation ────────────────┐
    │     (Portfolio math, analytics,        │
    │      provider resilience, guardrails)  │
    │                                        │
    └─── LLM Synthesis ──────────────────────┴──→ Output
         (Gemma 4 analysis)
              │
              └─── Narrative Polish ────────→ Final Response
                   (MiniMax or cloud LLM)
```

---

## Contributing

Before modifying the architecture:
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for current structure
2. Review [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) for principles
3. Check [ARCHITECTURE_MODELS.md](ARCHITECTURE_MODELS.md) if touching LLM integration
4. Update tests and documentation
5. Link your PR to the relevant architecture doc

---

**Last Updated**: April 2026  
**Maintainer**: @perlowja
