# Agentic COBOL — multi-flavor natural-language routing acceptance harness

> *Why we reverted to a 60-year-old testing pattern to validate 2026 agentic systems.*
> See `AGENTIC_COBOL_SPEC.md` for the full methodology.

## What this is

Agentic COBOL is the natural-language-query routing-acceptance pattern
for the InvestorClaw + InvestorClaude fleet. `nlq-prompts.json` is the
canonical prompt set; runners on each agent runtime consume it and emit
PASS/FAIL per scenario. 30 prompts × 4 runtimes = 120 routing decisions
per release cycle.

The methodology echoes COBOL's 1959 design ethos — domain expert speaks
business English, machine routes to the right operation — but accepts
that 2026's stochastic LLM substrate replaces COBOL's deterministic
parser. The acceptance pattern survives intact; the guarantees become
empirical (multi-trial sampling, per-runtime noise floors) instead of
compile-time.

**The test suite must run across all agent flavors.** Each prompt has
`expected_routes` keyed per runtime:

- `investorclaw` — the 9-tool consolidated surface used by OpenClaw /
  ZeroClaw / Hermes / standalone (per `SKILL.toml [[tools]]`)
- `investorclaude` — the Claude Code slash-command surface (currently
  ~25 granular `/investorclaude:ic-*` commands; v2.4 cycle consolidates
  this to the same 9-tool surface as InvestorClaw, after which both
  keys collapse)

## Runners (one per runtime family)

| Runtime | Runner | Mode |
|---|---|---|
| OpenClaw / ZeroClaw / Hermes | `harness/run_cross_runtime_pilot.py` | Automated `docker exec` |
| Claude Code (InvestorClaude) | `harness/cobol/cobol-barrage.sh` (in InvestorClaude repo) | `claude -p --plugin-dir` non-interactive |

Both runners read from this JSON. v2.4 cycle adds a single unified
report generator that aggregates all 4 runtime scores into one
release-evidence document.

## Per-runtime acceptance gates

Reflects each platform's LLM-routing noise floor on a multi-tool
surface. OpenClaw uses GRAEAE consensus orchestration (deterministic-ish);
the LLM-driven runtimes have observed ~80% noise floors on similar
surfaces; Hermes runs smaller models so its floor is lower.

| Runtime | min_pass (strict) | publish_bar |
|---|---:|---:|
| OpenClaw | 25/30 (83%) | 27/30 (90%) |
| ZeroClaw | 21/30 (70%) | 24/30 (80%) |
| Hermes | 17/30 (57%) | 20/30 (67%) |
| Claude Code | 21/30 (70%) | 24/30 (80%) |

These gates supersede the v2.1.9 baseline (10/10, 8/10, 6/10 on the
old 10-prompt set) and the v2.3.4 COBOL bar (9/15 strict, 12/15
publish on the 15-prompt set). Update gates per release as the
plateau moves.

## Adding a prompt

1. Append to the `prompts` array in `nlq-prompts.json`
2. Cover every relevant runtime in `expected_routes` (use `DEFLECT_OK`
   where the correct behavior is no portfolio command)
3. Bump `version` field (e.g. `2.4.0-alpha` → `2.4.0`)
4. Adjust `fleet_gates` if the surface area materially changes

## Running across all 4 flavors

```bash
# On linux-x86-host (containers must be up):
ssh user@192.0.2.61

# 1. InvestorClaw cross-runtime (OpenClaw + ZeroClaw + Hermes)
cd /home/user/InvestorClaw
uv run python harness/run_cross_runtime_pilot.py \
    --runtimes openclaw,zeroclaw,hermes \
    --output /tmp/cross-runtime-$(date +%F).json

# 2. InvestorClaude COBOL (Claude Code)
cd /home/user/InvestorClaude
bash harness/cobol/cobol-barrage.sh

# 3. Aggregate (v2.4 deliverable)
# python harness/cobol/aggregate-fleet-scores.py
```

## v2.3.x → v2.4.0 cycle

The architectural correction in flight:

- **InvestorClaude's 25 granular slash commands → 9 consolidated tools**
  matching InvestorClaw's existing surface (per SKILL.toml). Removes the
  "InvestorClaude is a special snowflake" ambiguity. Reduces Claude Code
  routing noise on the granular surface.
- **Single unified harness** consuming this JSON across all 4 runtimes.
- **Single aggregate report** per release with all 4 scores side-by-side.
