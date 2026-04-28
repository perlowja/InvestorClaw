# Agentic COBOL — Specification

**Status:** Draft v0.2 (2026-04-27 — adds Class A/B routing distinction and Class B safety-critical reference architecture)
**Editors:** Jason Perlow (perlowja), mac-dev-host personal-claude session
**Scope:** Fleet routing-acceptance methodology for agent-skill products.
Targets InvestorClaw, InvestorClaude, and any future fleet adapter that
exposes natural-language tool routing.

---

## 1. Abstract

Agentic COBOL is a testing methodology for products whose value
proposition is *"the agent picks the right tool from natural language."*
It treats the system under test as the **LLM-plus-tools combo** rather
than the tools alone, and evaluates whether the agent routes a corpus
of natural-language utterances to the expected backend operations.

The pattern revives COBOL's 1959 design ethos — domain expert speaks
business English, machine routes to the right operation — but accepts
that 2026's stochastic LLM substrate replaces COBOL's deterministic
parser. Compile-time guarantees become empirical sampling.

---

## 2. Problem statement

Modern testing pyramids assume the system under test is the code.
For agent-skill products, the system is the LLM-plus-tools combo.
Three failure modes that traditional testing misses:

1. **Silent misrouting.** The agent picks the wrong tool. Unit tests
   on each tool pass; the user-visible product is broken because the
   right tool is never invoked. Examples: a `news` command that
   doesn't get triggered for "any M&A news today?", a `lookup` command
   that doesn't fire for "what's NVDA worth?", a `setup` command that
   greedily preempts portfolio queries.

2. **Global attention shift.** Changing the description text of one
   command alters routing for *unrelated* commands, because LLM
   routing depends on the entire skill catalog at once. Per-component
   tests cannot detect this. Empirical example: tightening InvestorClaude's
   `ic-setup` description in v2.3.5→v2.3.6 caused regressions in
   `ic-bonds`, `ic-news`, `ic-lookup` — none of whose descriptions were
   touched.

3. **Cross-runtime variance.** The same prompt routes differently on
   Claude Code vs OpenClaw vs ZeroClaw vs Hermes. A test that passes
   on the dev machine can fail on the production runtime. Component
   tests run in process; routing tests must run in the deployed
   runtime + LLM combo.

Agentic COBOL addresses all three by making routing the unit of test.

---

## 3. Methodology

### 3.1 Acceptance pattern

The acceptance pattern depends on the product's routing class.

**Class A (best-effort routing) — routing acceptance:**

1. **Given** a runtime is loaded with the system under test.
2. **When** the user submits a natural-language utterance.
3. **Then** the agent should invoke a backend operation matching
   one of the scenario's `expected_routes`.

A scenario PASSES if any expected route is invoked. Deflection
scenarios PASS if no portfolio command is invoked (tracked via the
`DEFLECT_OK` sentinel in `expected_routes`).

**Class B (safety-critical routing) — verbatim-narrative acceptance:**

The Class B pattern is fundamentally different because routing
decisions are absent (every command always runs). The acceptance
test instead validates that the narrator quotes the envelope verbatim:

1. **Given** a runtime is loaded with the system under test, and a
   pre-computed envelope with known section data.
2. **When** the user submits a natural-language utterance.
3. **Then** the narrator's response should:
   a. Quote ONLY numbers that appear verbatim in the envelope, AND
   b. Reference data appropriate to the question's intent
      (`expected_focus_section` matches a section the narrator drew
      from), AND
   c. Refuse appropriately when data is out-of-envelope (instead of
      fabricating).

A scenario PASSES if (a) AND (b) AND (c) all hold. Each scenario in
`nlq-prompts.json` for a Class B product carries `expected_focus_section`
in addition to (or instead of) `expected_routes`. Programmatic
fabrication detection: every numeric claim in the response is
verified against the envelope by exact-substring match.

### 3.2 Empirical sampling

Because the LLM substrate is stochastic, single-trial scoring is
unreliable. Recommended:

- **Per-trial:** record the routing decision for one prompt invocation.
- **Per-prompt:** average over 3 trials, take majority routing.
- **Per-release:** report per-runtime score and 95% CI.

For dev iteration (turnaround speed > certainty), single-trial scoring
is acceptable but should be flagged as such in reports.

### 3.3 Per-runtime gates — by routing class

Acceptance gates depend on the **routing class** of the product, which
determines how reliable routing must be:

#### Class A: Best-effort routing

For products where misrouting is annoying but recoverable
(developer tools, content generation, casual chat plugins). LLM noise
floors are accepted; gates are sub-100% and per-runtime.

| Runtime | Substrate | Strict floor | Publish bar |
|---|---|---:|---:|
| OpenClaw | GRAEAE consensus orchestration | 25/30 (83%) | 27/30 (90%) |
| ZeroClaw | LLM-driven (configurable provider) | 21/30 (70%) | 24/30 (80%) |
| Hermes | Smaller-model LLM | 17/30 (57%) | 20/30 (67%) |
| Claude Code | LLM-driven (Anthropic) | 21/30 (70%) | 24/30 (80%) |

Empirical evidence backing these gates comes from the v2.3.x → v2.4.0
cycle: description tuning plateaued at 12/15 (80%) on Claude Code; the
v2.4.0 architectural consolidation (27 commands → 13) measured 19/30
(63%) — all in the LLM-routing-noise band. Class A gates are *what
description tuning can achieve*.

#### Class B: Safety-critical routing

For products where misrouting can cause real-world harm — financial
data, medical information, legal advice, infrastructure operations,
anything where a fabricated answer or wrong tool selection has user
cost. **Class B gates are 100% across all runtimes, achieved
architecturally, NOT through description tuning.**

| Runtime | Substrate | Strict floor | Publish bar |
|---|---|---:|---:|
| OpenClaw | Deterministic-engine + verbatim-narrator | 30/30 (100%) | 30/30 (100%) |
| ZeroClaw | Deterministic-engine + verbatim-narrator | 30/30 (100%) | 30/30 (100%) |
| Hermes | Deterministic-engine + verbatim-narrator | 30/30 (100%) | 30/30 (100%) |
| Claude Code | Deterministic-engine + verbatim-narrator | 30/30 (100%) | 30/30 (100%) |

The architectural pattern that achieves Class B (see §3.4):

1. **Eager precomputation.** Every relevant backend command runs
   *before* the LLM sees the user's prompt. Output is a single
   HMAC-signed JSON envelope.
2. **Verbatim-narrator constraint.** The LLM only narrates from the
   envelope. It is strictly prompted to quote numbers verbatim and
   refuse to supplement from training data.
3. **Programmatic verification.** Every numeric value in the
   narrator's output must be findable in the envelope; mismatches
   raise a fabrication error and the response is rejected.

The routing decision evaporates because the router class becomes
"every command always runs." The LLM's role narrows from "router +
narrator" to just "narrator over verified data" — a much easier
problem with much higher reliability.

#### Choosing a class

```
Could a misrouted answer cause measurable user harm
(financial loss, health risk, legal exposure, lost work)?
  ├─ Yes → Class B (safety-critical, 100% gates, deterministic + verbatim)
  └─ No → Class A (best-effort, per-runtime gates, LLM-routed)
```

For the InvestorClaw + InvestorClaude fleet, Class B is the correct
class (personal financial data; misrouting could lead the user to
make decisions on fabricated numbers). The v2.5 cycle migrates the
fleet from Class A to Class B.

### 3.4 Class B reference architecture: deterministic-engine + verbatim-narrator

```
User prompt arrives
    ↓
Plugin checks envelope cache (per-portfolio, per-section TTLs)
    ↓
If cache miss → emit user-facing wait message
                ("Running your portfolio analysis through ic-engine.
                  The deterministic pipeline is computing holdings,
                  performance, bonds, analyst data, news, and risk
                  synthesis from authoritative sources — this takes
                  30-60 seconds the first time you ask. Subsequent
                  questions in this session will use the cached data
                  and respond instantly. Please wait.")
              → fire `investorclaw run --all` (parallel pipeline:
                holdings + performance + bonds + analyst + news +
                synthesize + optimize + cashflow + peer)
              → wait for envelope OR partial envelope on per-section
                failure
    ↓
Pass envelope + user prompt to verbatim-narrator
    ↓
Narrator system prompt enforces:
  1. Use ONLY data from this JSON envelope. Quote numbers VERBATIM.
  2. If user asks about something not in envelope → refuse + tell
     them which command would fetch it.
  3. NEVER infer, estimate, supplement, or substitute from training data.
  4. Include the envelope's ic_result.hmac in the response footer.
    ↓
Narrator output passes through fabrication validator:
  - Every dollar amount, percentage, ratio, or numeric claim in the
    output must be findable verbatim in the envelope.
  - Failures raise FabricationError; canned refusal message shown
    to user.
    ↓
Reply (with HMAC provenance footer)
```

Key properties of this architecture:

- **Routing is structurally absent.** Every command runs eagerly. The
  LLM never picks between commands; it picks how to *narrate* over a
  fixed dataset. The 80% noise floor that bounded Class A doesn't
  apply.
- **Fabrication is structurally impossible.** The narrator's only data
  source is the envelope. Validation catches any numeric claim that
  doesn't appear verbatim in the envelope.
- **Provenance is auditable.** Every response carries an HMAC hash
  pointing to the envelope it was narrated from; the envelope itself
  is signed and timestamped.
- **Refusal beats fabrication.** When data is missing, the narrator
  refuses + recommends a command. Users get "I don't know" instead of
  "here's a made-up number."
- **Cache amortizes the cost.** First prompt of a session: 30-60s
  wait while the pipeline runs. Subsequent prompts: instant
  cache-hit, narrator only.

This is the v2.5 fleet target architecture.

---

## 4. Prompt format

### 4.1 Canonical JSON

`nlq-prompts.json` is the canonical exchange format. Each prompt:

```json
{
  "id": "p01-holdings-1",
  "intent": "portfolio-snapshot",
  "prompt": "What is in my portfolio right now?",
  "expected_routes": {
    "investorclaw": ["portfolio_view section=holdings", "holdings"],
    "investorclaude": ["portfolio-view holdings", "portfolio-run"]
  }
}
```

- `id` — stable scenario identifier across releases.
- `intent` — taxonomic group (used for aggregate reporting).
- `prompt` — the natural-language utterance verbatim.
- `expected_routes` — Class A only. Runtime-keyed list of acceptable
  invocations. Multiple routes per runtime represent OR; any match is
  a pass.
- `DEFLECT_OK` (string) — Class A deflection sentinel; pass if no
  portfolio command is invoked.
- `expected_focus_section` — Class B only. The envelope section the
  narrator should draw data from when answering this prompt. Used by
  the Class B verbatim-narrative validator to confirm the response
  references the right section (e.g., a "what's my Sharpe?" prompt
  should produce a narrative that cites `envelope.sections.performance`,
  not `envelope.sections.bonds`).
- `expected_refusal` (boolean) — Class B only. If true, the prompt
  should trigger the narrator's out-of-envelope refusal pattern. The
  validator passes the scenario when the response matches the canned
  `NARRATOR_OUT_OF_SCOPE` or `NARRATOR_FABRICATION_REFUSAL` text from
  `ic_engine.config.user_messages`.

### 4.2 Optional Gherkin emission

The same scenarios can be emitted as Gherkin `.feature` files for
teams using `pytest-bdd` / `behave` / `cucumber`. The mapping is
mechanical:

```gherkin
Feature: Portfolio holdings — natural-language routing
  Scenario: User asks what's in their portfolio (p01-holdings-1)
    Given the InvestorClaude plugin is loaded on Claude Code
    When the user asks "What is in my portfolio right now?"
    Then the agent should invoke "portfolio-view holdings"
    Or invoke "portfolio-run"

  Scenario: User asks what's in their portfolio (p01-holdings-1) [investorclaw]
    Given the InvestorClaw skill is loaded on OpenClaw
    When the user asks "What is in my portfolio right now?"
    Then the agent should invoke "portfolio_view section=holdings"
    Or invoke "holdings"
```

A reference emitter (`tools/emit-gherkin.py`) is planned for v2.5;
runners that prefer Gherkin can adopt it without changes to the
canonical JSON. The JSON stays authoritative.

### 4.3 Naming conventions

- `pNN-<intent>-<variant>` for scenario IDs (e.g., `p01-holdings-1`,
  `p02-holdings-2`).
- `intent` slugs use kebab-case (e.g., `portfolio-snapshot`,
  `bond-strategy`, `deflect-concept`).
- Prompts use ASCII English only (no smart quotes, no unicode
  punctuation) for cross-runtime compatibility.

---

## 5. Runner contract

A conforming Agentic COBOL runner MUST:

1. **Read prompts** from a path supplied by the caller (default:
   `harness/cobol/nlq-prompts.json` relative to the fleet root).
2. **Filter by runtime key** — emit only scenarios where
   `expected_routes[runtime]` is non-empty.
3. **Invoke the agent** with the prompt verbatim. No reformatting,
   no system-prompt injection, no role-play scaffolding.
4. **Capture the routing decision** — slash command invocation,
   bash tool invocation, or explicit textual reference to the
   expected route.
5. **Score per scenario** — emit JSONL with `{id, prompt, expected,
   detected, passed, runtime, latency_ms}`.
6. **Emit aggregate** — total scenarios, passed count, gate pass/fail.

Runners SHOULD:

- Support `--trials N` for empirical sampling.
- Support `--runtime <name>` for filtering.
- Emit a stable JSONL schema versioned alongside the prompt set.

Runners MAY:

- Cache responses for development workflows.
- Add per-prompt timeouts.
- Emit Gherkin feature files for downstream tooling.

### 5.1 Reference runners

| Path | Runtime(s) | Status |
|---|---|---|
| `InvestorClaw/harness/run_cross_runtime_pilot.py` | OpenClaw / ZeroClaw / Hermes | v0.x — needs nlq-prompts.json refactor (v2.4 work) |
| `InvestorClaude/harness/cobol/cobol-barrage.sh` | Claude Code | v0.x — `claude -p --plugin-dir` non-interactive |

Both will share a JSONL output schema and feed the v2.4 aggregate
report generator.

---

## 6. Versioning

`nlq-prompts.json` carries a top-level `version` field following
semver:

- **Major** — breaking change to scenario IDs or `expected_routes`
  schema. All runners must update.
- **Minor** — added scenarios. Runners that ignore unknown IDs
  continue working.
- **Patch** — clarification, typo fix, gate adjustment. No runner
  changes needed.

Per-release fleet evidence references the prompt-set version at
test time, e.g. `v2.4.0 release ran NLQ v2.4.0-alpha against fleet`.

---

## 7. Migration from existing tools

### 7.1 From bare unit tests

Add Agentic COBOL alongside, not as a replacement. Unit tests stay
authoritative for component correctness; Agentic COBOL adds the
routing acceptance layer.

### 7.2 From pytest-bdd / behave

Both can consume `.feature` files emitted from `nlq-prompts.json`.
The fleet's canonical exchange format is JSON; teams using BDD
runners convert at runtime via the planned `tools/emit-gherkin.py`.

### 7.3 From custom routing tests

Most pre-existing routing tests are some form of Agentic COBOL
without the formalism (e.g., InvestorClaw's pre-v2.4
`run_cross_runtime_pilot.py` had 10 hardcoded prompts with expected
tool sets). Migration is mechanical: extract prompts to the canonical
JSON, refactor the runner to consume it.

---

## 8. Why Agentic COBOL (vs. modern alternatives)

The COBOL framing is deliberate:

1. **Same problem.** COBOL's design goal — domain expert speaks
   English, machine routes to operation — is exactly the problem
   agent-skill products face today.
2. **Same acceptance pattern.** "Read the prompt aloud, check the
   system did the right thing" is the test methodology in both eras.
3. **Different substrate.** COBOL's parser was deterministic; LLMs
   are stochastic. The methodology survives; the guarantees become
   empirical.

Compared to alternatives:

- **Pure BDD/Gherkin** is the right *structural* pattern (we adopt
  Given/When/Then internally) but doesn't articulate the
  natural-language-routing acceptance focus.
- **LLM-eval frameworks (RAGAS, DeepEval)** focus on output quality.
  Agentic COBOL focuses on tool selection — orthogonal layer.
- **Component tests** prove tools work in isolation; can't catch
  silent misrouting.
- **End-to-end tests** without natural-language coverage miss the
  routing-decision class of bug entirely.

The "60-year-old language solving a 2026 problem" framing is correct
*in spirit*: a 1959 design pattern (English-as-interface, machine-as-
router) is the right pattern for 2026 agentic systems. The substrate
got fuzzier; the test methodology survives.

---

## 9. Open questions

- **Multi-trial reporting:** Class A spec defaults to single-trial for
  dev speed but recommends 3-trial averaging for releases. Class B
  doesn't need multi-trial because the routing is deterministic (cache
  hits + verbatim narration produce identical responses across trials).
- **Prompt corpus governance:** as the corpus grows past 30 prompts,
  who owns review of new additions? Likely fleet-maintainer + per-skill
  contributor approval.
- **Cross-runtime parity scoring:** for Class B, parity is structural
  (same envelope, same narrator → same answer regardless of host
  runtime). For Class A, cross-runtime parity remains an open metric.
- **Non-English prompts:** spec is English-only at v0.1. i18n is a
  v1.x consideration.
- **Adversarial prompts:** out-of-domain queries, prompt-injection
  attempts. Could be a separate `adversarial-prompts.json` corpus.
- **Class B narrator-LLM choice:** the verbatim constraint is provider-
  agnostic, but smaller models are easier to keep on-rails than larger
  ones (less likely to "creatively interpret" the strict prompt).
  Whether to mandate a model class for Class B narrators is open.
- **Envelope-section-level Class B/Class A mix:** could a single
  product have Class B sections (financial numbers) AND Class A
  sections (general market commentary)? Probably yes; the spec doesn't
  preclude it. Per-section classification deferred to v0.2.

---

## 10. References

- COBOL specification (1959, ANSI X3.23-1968)
- Gherkin / Cucumber BDD docs — github.com/cucumber/cucumber
- pytest-bdd — pytest-bdd.readthedocs.io
- InvestorClaw fleet harness — `harness/cobol/`
- InvestorClaude COBOL barrage — `harness/cobol-barrage.sh`
- Companion blog draft — `BLOG_DRAFT_techbroiler.md`

---

*This spec is draft v0.1. Comments and revisions welcome via the
fleet harness PR flow. v1.0 target: end of v2.4 cycle, with
empirical fleet-wide evidence backing the per-runtime gates.*
