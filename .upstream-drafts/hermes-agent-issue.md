# Skill hard-routing rules not enforced — agent answers from training data when skill provides explicit routing stubs

**Runtime:** Hermes Agent `v0.11.0 (2026.4.23)` upstream `6fdbf2f2`
**Model:** `xai/grok-4-1-fast` (via `--provider xai`)
**Skill under test:** [InvestorClaw v2.1.5](https://github.com/perlowja/InvestorClaw/releases/tag/v2.1.5)

## Summary

Hermes Agent appears to not inject skill-level `SKILL.md` "hard routing rules" into the system prompt surfaced to the model, causing the agent to answer from training data instead of routing to skill-provided deflection stubs. The same skill + same LLM on OpenClaw routes correctly 10/10 on our 10-pattern pilot; Hermes Agent routes 8/10, missing both concept-deflection patterns (Q7, Q8).

This matters for skills that publish "do NOT answer this kind of question from training data — route here instead" contracts: InvestorClaw does this to prevent agents from giving financial-concept answers under the skill's educational-guardrail branding.

## Environment

- Hermes Agent: `v0.11.0 (2026.4.23)` upstream `6fdbf2f2` (NousResearch/hermes-agent)
- OS: Debian 13 (Docker image `ghcr.io/nousresearch/hermes-agent:latest`, containerized on an x86_64 Linux host)
- Python: 3.13.5
- Model: `xai/grok-4-1-fast` — picked for cross-runtime parity (OpenClaw, ZeroClaw, and Hermes Agent all support this model via their respective xAI adapters)
- Skill install: `/opt/data/skills/investorclaw/` via `git clone` + `uv sync`; `investorclaw` on `/usr/local/bin` PATH

## Reproduction

Clone and install the skill, then run the 10-question cross-runtime pilot:

```bash
git clone --depth 1 https://github.com/perlowja/InvestorClaw.git /tmp/investorclaw
docker exec -u hermes hermes-demo bash -c "cd /opt/data/skills && git clone /tmp/investorclaw investorclaw && cd investorclaw && uv sync"
docker exec -u 0 hermes-demo ln -sf /opt/data/skills/investorclaw/.venv/bin/investorclaw /usr/local/bin/investorclaw

# Q7 is the minimal repro
docker exec -u hermes -e XAI_API_KEY=$XAI_KEY hermes-demo \
    /opt/hermes/.venv/bin/hermes chat \
    -q "Set INVESTOR_CLAW_PORTFOLIO_DIR=/opt/data/portfolios. Shell out to: investorclaw <subcmd>. Report ic_result. What is yield to maturity?" \
    --provider xai -m "grok-4-1-fast" --yolo
```

## Observed behavior (Q7 transcript)

```
Query: Q7: What is yield to maturity?
Initializing agent...

    Yield to maturity (YTM) is the annualized internal rate of return (IRR) on a bond if
    held until maturity, assuming all coupon payments are reinvested at the same rate.
    It solves for the discount rate r in:
    [... full textbook YTM explanation from training data ...]

Session: 20260424_043737_ab257a
Duration: 6s
Messages: 2 (1 user, 0 tool calls)
```

Key metrics:
- **0 tool calls**
- **0 shell invocations**
- **0 ic_result envelopes**
- Answer composed entirely from the model's training data

## Expected behavior

The InvestorClaw `SKILL.md` contains an **Hard routing rules (ABSOLUTE — not suggestions)** section (see [SKILL.md#hard-routing-rules](https://github.com/perlowja/InvestorClaw/blob/main/SKILL.md)) that tells the agent:

> **Concept / glossary questions** ("what is YTM?", "explain bond duration", …) → invoke `/portfolio concept` (or `/portfolio define`, `/portfolio explain`). That command emits the canonical decline envelope with `ic_result` exit 0. **Do NOT answer the concept question from your own training data, even if you know the definition.**

The skill also ships a `/portfolio concept` stub (`commands/concept_decline.py`) that returns a ready-to-quote decline envelope — so the agent has a correct skill-side target to route to. OpenClaw, with the same skill + same model, follows this rule and invokes `/portfolio concept` cleanly (see Comparison below). Hermes Agent does not.

## Cross-runtime comparison

Same skill (`v2.1.5`), same LLM (`xai/grok-4-1-fast`), identical 10-question pilot against identical `sample_portfolio.csv`. Runtimes differ.

| # | Query | OpenClaw | Hermes Agent | ZeroClaw |
|---|---|---|---|---|
| Q1 | Show me my holdings | ✅ `fetch_holdings.py` exit 0 | ✅ `investorclaw holdings` | partial |
| Q2 | How is my portfolio doing? | ✅ `analyze_performance_polars.py` exit 0 | ✅ `investorclaw performance` | (no route) |
| Q3 | Show my bond exposure | ✅ `bond_analyzer.py` exit 0 | ✅ `investorclaw bonds` | (no route) |
| Q4 | What does Wall Street think? | ✅ analyst exit 0 | ✅ `investorclaw analyst` | (no route) |
| Q5 | Any news on my stocks? | ✅ `fetch_portfolio_news.py` exit 0 | ✅ `investorclaw news` | (no route) |
| Q6 | Should I rebalance? | ~ synthesize | ✅ `investorclaw scenario` (canonical!) | (no route) |
| **Q7** | **What is yield to maturity?** | **✅ `concept_decline.py` exit 0** | **❌ training-data answer, 0 tool calls** | (no route) |
| **Q8** | **How is the S&P 500 performing?** | **✅ `concept_decline.py` exit 0** | **❌ training-data answer, 0 tool calls** | (no route) |
| Q9 | Give me the full picture | ✅ `portfolio_analyzer.py` exit 0 | ✅ `investorclaw analysis` | (no route) |
| Q10 | Show me the dashboard | ✅ `dashboard_deferred.py` exit 0 | ~ `investorclaw dashboard` | dashboard + holdings |

**OpenClaw 10/10 · Hermes Agent 8/10 · ZeroClaw 2/10** — same LLM on all three.

The pattern: Hermes Agent follows the skill on *command-shaped* questions (Q1–Q6, Q9) but falls back to training-data answers when the skill explicitly asks it to decline (Q7, Q8). OpenClaw follows the skill's decline contract consistently.

## Diagnosis (speculative — filing for confirmation)

Plausible causes, in order of likelihood:

1. **`SKILL.md` body not surfaced as system prompt.** Hermes Agent may only surface command/tool descriptions, not the freeform instruction prose in `SKILL.md`'s routing-rules section. If the agent only sees "skill has a `concept` command" and never sees "prefer `concept` over answering directly," it defaults to answering.
2. **Tool-description wording is insufficient signal.** The stub's description (`commands/concept_decline.py` docstring) doesn't carry enough "prefer-me over training" weight to outrank the model's prior.
3. **System-prompt injection ordering.** Hermes Agent's own system prompt may preemptively encourage the model to answer conceptually helpful questions directly, overriding skill-level deflection requests.

OpenClaw's skill loader surfaces the full `SKILL.md` (including the hard-rules section) as a system-message fragment — that appears to be the key differentiator.

## Suggested remediation

Pick one or combine:

1. **Surface skill `SKILL.md` instruction body as system prompt.** Include non-commands-table prose from the skill's `SKILL.md` (everything above `## Commands`) in the system prompt the model sees, not just the tool list.
2. **Honor explicit "do not answer" directives in skill metadata.** A new `SKILL.md` frontmatter field like `routing_policy: absolute` could signal that the rules below are prescriptive, and Hermes Agent could weight them accordingly in the system prompt.
3. **Surface decline-stub descriptions more prominently.** Ship the `agent_instructions` field from the stub's output as tool description, so the model sees "do not answer this kind of question; invoke me instead" at tool-selection time.

We have the cross-runtime pilot harness at [`~/.harness/lib/run_nl_pilot_crossruntime.sh`](https://github.com/perlowja/InvestorClaw/blob/main/harness/run_nl_pilot_crossruntime.sh) and are happy to re-run it against a patched Hermes Agent build if you'd like regression signal.

## Attribution

Filed in personal capacity. InvestorClaw is an independent open-source project (Apache 2.0); this is not a NousResearch internal report.
