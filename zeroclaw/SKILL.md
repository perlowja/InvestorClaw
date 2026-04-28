---
name: investorclaw
version: "2.5.0"
description: FINOS CDM 5.x-compliant deterministic-first portfolio analysis for InvestorClaw, installed as a ZeroClaw skill. Ask natural-language portfolio questions through `investorclaw ask "<question>"`; the engine eagerly runs the deterministic pipeline, stores an HMAC-signed JSON envelope, and narrates verbatim from authoritative outputs. Use `investorclaw refresh` to force fresh prices/news/cache. Educational output only — not investment advice.
license: "Apache-2.0"
compatibility: "ZeroClaw runtime; Python 3.10+ available in the surrounding host or container"
homepage: https://gitlab.com/argonautsystems/InvestorClaw
user-invocable: true
metadata:
  author: "Jason Perlow <jperlow@gmail.com>"
  tags:
    - portfolio-analysis
    - holdings
    - bonds
    - analyst-consensus
    - finos-cdm
    - guardrails-compliant
    - educational-output
    - zeroclaw
  languages:
    - python
  frameworks:
    - zeroclaw
  domain: finance
---

# InvestorClaw Portfolio Analysis

Educational portfolio analysis using live market data via Yahoo Finance (free tier).
All output is informational only — not personalized investment advice.

## When to use
- User asks natural-language portfolio or finance questions
- Portfolio analysis, holdings summary, bond analytics, performance review, sector breakdown
- Financial news for held positions or market-wide news by topic

## Environment Setup

Ask InvestorClaw to set up or detect portfolio files through the deterministic
surface. The operation is idempotent.

```bash
investorclaw ask "Set up InvestorClaw and detect my portfolio files"
```

Expected: setup summary, or "Setup already complete. Skipping."

## Commands

All commands use the canonical `investorclaw` CLI entry point. The v2.5.0
agent surface has two commands:

```bash
investorclaw ask "What's in my portfolio?"
investorclaw ask "How am I doing?"
investorclaw ask "Show my bond exposure"
investorclaw ask "Generate my end-of-day report"
investorclaw refresh
```

`investorclaw ask` eagerly runs the required backend commands, stores the
HMAC-signed JSON envelope, and narrates from authoritative output.
`investorclaw refresh` forces fresh prices/news/cache when requested.

## Hard routing rules (ABSOLUTE — not suggestions)

These rules exist because NL-pilot testing showed the agent will otherwise
answer from training data, producing responses that look authoritative but
lack `ic_result` verification. Do not bypass them even if you are confident
you know the answer.

- **Concept / glossary questions** ("what is YTM?", "explain bond
  duration", "define alpha", "what does Sharpe ratio measure?") →
  invoke `investorclaw ask "<question>"`. **Do NOT answer the concept question from
  your own training data, even if you know the definition.**
- **Market-wide / macro questions** ("how is the S&P 500 performing?",
  "what's the Fed doing?", "VIX level?") → invoke `investorclaw ask "<question>"`.
- **Market-wide NEWS questions** ("any crypto news?", "M&A headlines?",
  "forex updates?", "general market news?") → invoke `investorclaw ask "<question>"`.
- **Dashboard requests (narrow trigger only)** — invoke
  `investorclaw ask "<question>"` when the user uses the literal word
  "dashboard" or asks for "the 15-tab view" / "PWA" / "visual interface."
- **Rebalancing questions** ("should I rebalance?", "do I need to
  rebalance?") → invoke `investorclaw ask "<question>"`.
- **Freshness requests** ("refresh my prices", "force a fresh run") →
  invoke `investorclaw refresh`.

## Anti-Fabrication Rules

1. **Always execute the command and use its actual output** — never generate portfolio data from memory or prior sessions
2. If a command fails, report the exact error — do not fabricate a success response
3. All output is educational/informational — include the disclaimer: "EDUCATIONAL ANALYSIS - NOT INVESTMENT ADVICE"
4. Do not cache or reuse output from a previous `investorclaw ask` run when the user asks for fresh data
5. If the entry point is not available, run `pip install .` from the InvestorClaw directory and retry

## ic_result verification

Every verified command emits a terminal JSON envelope as the last stdout line:

```json
{"ic_result":{"command":"ask","engine":"ic-engine","exit_code":0,"duration_ms":1420}}
```

- Echo `ic_result.exit_code` in every response that invokes a command.
- Absence of `ic_result` = UNVERIFIED — state this explicitly.
- Do not reconstruct or narrate a hypothetical result for missing output.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `investorclaw: command not found` | Run `pip install .` from InvestorClaw dir |
| `ModuleNotFoundError: No module named 'ic_engine'` | Run `uv sync` or `pip install .` from the InvestorClaw directory |
| `Quote not found for symbol: SAMPLE_FUND` | Expected — Fidelity-style fund not in Yahoo Finance |
| `No portfolio CSV found` | Copy CSV to `~/portfolios/` or ask InvestorClaw to set up portfolio discovery |
| API rate limit | Wait 5–10 min and retry |
