# Blog draft — Agentic COBOL

**Landing zone:** techbroiler.net
**Status:** draft with v2.5.x empirical numbers (2026-04-28)
**Target length:** 1500-2500 words
**Authors:** Jason Perlow + agent collaborators
**Tags:** agentic-systems, llm, testing, plugin-ecosystem, cobol, bdd

---

## Working title (pick one)

- **Agentic COBOL: Why we reverted to a 60-year-old language to test 2026 agentic systems**
- *We tested our LLM agent with COBOL. Here's why it worked.*
- *The acceptance test pattern your unit-test suite is missing*
- *Compile-time guarantees were nice. Now we sample.*

---

## Hook (paragraph 1-2)

Last week our CI was green and our agent was broken.

Every Python unit test passed. Every component returned correct JSON.
The harness contract gate said `status=pass`. The plugin manifest
validated. And every time a user said "what's in my portfolio
right now?", Claude Code would shrug and offer to set up the plugin —
even though the plugin was already loaded and working.

The bug wasn't in the code. The bug was that the agent never **chose**
the right tool.

Modern testing pyramids assume the system under test is the code. For
agent-skill products, the system is the LLM-plus-tools combo. We needed
a different kind of test, and the pattern we landed on was older than
the World Wide Web — older than UNIX, older than the ARPANET. We needed
COBOL.

---

## Section 1 — The silent-misroute class of bug (300-400 words)

Walk through a concrete example:

- The user asks: *"Any big mergers or acquisitions in the news today?"*
- The plugin has an `ic-news` command with a tested Python implementation
  that fetches M&A headlines correctly. Unit tests on the function pass.
- The agent doesn't invoke `ic-news`. Doesn't invoke anything. Answers
  from training data. The user gets stale data the agent made up.

How did this happen? The `ic-news` description was three words:
"News headlines fetcher." That's accurate but invisible to the LLM
routing decision. "M&A" wasn't in the description. "Mergers" wasn't.
"Today" wasn't. The agent had no signal that this command was relevant.

This is the silent-misroute class of bug. It's not a code bug. It's not
a logic bug. It's a *description-as-API* bug — the LLM-facing surface
of the tool was undercommunicated. Unit tests can't see it because the
LLM isn't in their loop.

This class is ubiquitous in plugin / skill / MCP-server ecosystems.
Every product whose value proposition is "agent picks the right tool
from natural language" has it. And every CI suite that doesn't include
the LLM in the test loop is blind to it.

---

## Section 2 — Why modern testing tools don't catch it (300-400 words)

A unit test on `investorclaw news` proves the function works. It can't
prove the agent **calls** the function when a user asks about news.

A type-checker proves the API surface is well-formed. It can't prove
the description text triggers routing.

An end-to-end test with hardcoded inputs proves a happy-path scenario.
It can't enumerate the natural-language space well enough to catch
edge cases like "M&A news" → ghost route.

LLM-eval frameworks (RAGAS, DeepEval, etc.) measure **output quality**:
is the agent's answer factually correct, coherent, hallucinated? They
don't measure **tool selection** — orthogonal layer. The agent can
produce a beautifully hallucinated answer with zero tool calls and
score perfectly on output-quality metrics.

The class of bug we needed to catch was upstream of output: did the
agent invoke the *right tool* for the *right prompt*?

---

## Section 3 — Going back to first principles (400-500 words)

COBOL was designed in 1959 by Grace Hopper's committee with one explicit
goal: a domain expert (an accountant, a manager) should be able to read
the source code and verify the program does what they expect.

```cobol
ADD MONTHLY-PAY TO YEAR-TO-DATE-EARNINGS GIVING NEW-TOTAL.
IF NEW-TOTAL > BONUS-THRESHOLD THEN PERFORM CALCULATE-BONUS.
```

That's not pseudocode. That's executable COBOL. The acceptance test
was the readability of the source itself: an accountant could look at
the code, read it aloud, and judge whether it represented what they
asked for.

The pattern was **English-as-interface, machine-as-router**. The
domain expert speaks; the machine routes to the right operation. The
acceptance test is "read the prompt aloud and check the system did
what was asked."

That is *exactly* the problem we have with agent-skill products in
2026. A user types natural language; the agent routes to the right
tool; the test is "did the agent route correctly?"

The substrate changed. COBOL's parser was deterministic — it parsed
or it errored. LLMs are stochastic — same prompt, different routing
across runs, ~80% noise floor on a tuned surface. So compile-time
guarantees become empirical sampling. Multi-trial averaging. Per-runtime
gates.

But the **methodology** transfers cleanly: write down the prompt,
write down what the system should do, run it, score whether it did.

We called the resulting test pattern **Agentic COBOL**.

---

## Section 4 — The harness in practice (400-500 words)

Show the actual canonical prompt set:

```json
{
  "id": "p16-news-merger",
  "intent": "news-merger",
  "prompt": "Any big mergers or acquisitions in the news today?",
  "expected_routes": {
    "investorclaw": ["portfolio_market section=news topic=merger", "market"],
    "investorclaude": ["portfolio-view news", "portfolio-market news"]
  }
}
```

30 prompts. 4 runtimes (OpenClaw, ZeroClaw, Hermes, Claude Code). Each
prompt has runtime-specific expected routes because the same product
exposes a different surface in each runtime.

Walk through the v2.3.x → v2.5.x cycle as the empirical narrative:

- **v2.3.4 (15-prompt baseline):** 9/15 = 60% on Claude Code. Eight
  failures. All silent misroutes — agent answered without invoking
  the right tool.
- **v2.3.5 (description tuning):** 12/15 = 80%. Three remaining
  failures all looked like *over-routing* — `ic-setup` was greedily
  matching every portfolio query.
- **v2.3.6 (narrowed setup):** 11/15 = 73%. Three new regressions in
  commands whose descriptions weren't even touched. Discovery: LLM
  routing has a global attention layer; tightening one description
  shifts attention across the whole catalog.
- **v2.3.7 (rebalanced description weights):** 12/15 = 80%. Different
  failure mix. Plateau confirmed.
- **v2.4.0 (architectural correction):** 27 granular commands → 9
  consolidated tools. Claude Code 19/30 = 63% on the new 30-prompt
  set. Better surface, lower score: the new corpus exposes failure
  modes the 15-prompt set didn't reach.
- **v2.5.0 (adapter consolidation onto ic-engine v2.5.0):** Claude
  Code 24/30 = 80%. Five failures clustered on news/market deflects
  and cross-skill ambiguity (`investorclaude` vs `investorclaw`).
- **v2.5.1 (slash surface collapsed to `ask` + `refresh`):** Routing
  is finally tight. But the *measurement* breaks — see sidebar.
- **v2.5.2 (initial published release):** Claude Code **30/30 = 100%**.
  Cross-runtime: **OpenClaw 26/30 (86%) STRICT_PASS, Hermes 23/30
  (76%) PUBLISH** — both above min_pass, with provider stack switched
  to Together MiniMax-M2.7 for narrative + local gpu-host gemma-4-E4B
  for consultation (gemini quota stress on prior runs).

The plateau at 12/15 was *the signal*. Description tuning couldn't
break past it because the surface was structurally too granular —
27 commands competing for the same prompts. The fix wasn't more
tuning; it was consolidation.

That's a finding you don't get from any other test methodology.

---

### Sidebar — When the test fixture lies

The v2.5.1 → v2.5.2 jump from "1/30" to "30/30" *on the same recorded
agent runs* is the most uncomfortable lesson of this cycle.

The harness records every prompt's full agent transcript. The
v2.5.1 scorer parsed `claude -p --output-format=stream-json` events
looking for tool invocations on `Bash` or directly-named slash-command
tool calls. It missed the actual shape Claude Code now ships: plugin
slash commands surface as a `Skill` tool call with `input.skill =
"investorclaw:ask"`. The slash name lives in the input, not the tool
name.

The agent had been routing perfectly the entire time. The scorer
hadn't.

Rescoring the captured stream-json with a fixed `Skill`-aware
extractor turned the 1/30 (fail-the-publish-bar) into 30/30 (sail
past it). Same agent. Same prompts. Same model. Different lens.

The discipline that protects you here: **always commit the raw
artifact**. The `tool_invocations` field in the JSONL is the truth;
`detected` is the interpretation. When you can prove the
interpretation was wrong without re-running the agent, you have a
shippable fix; when you have to re-run, you've already lost a day to
provider quotas.

The test pyramid for agentic systems needs a layer the unit-test
era never had: **scorer correctness**. Treat the scorer like
production code. Test it against recorded transcripts. Version
its detection logic. Make it auditable.

(For our case the proof was a 30-row regression test that runs
the buggy v2.5.1 logic alongside the fixed v2.5.2 logic against
the recorded JSONL — old logic must reproduce 1/30, new logic
must hit 30/30. Both invariants are asserted on every CI run.
The test is in `harness/cobol/test_parse_stream_json.py`.)

---

## Section 5 — When this matters / who should use it (200-300 words)

Anyone whose product is "the agent picks the right tool from natural
language."

- Claude Code plugin authors
- OpenClaw / Anthropic skill builders
- MCP server developers
- Cursor / Windsurf / Codex CLI extensions
- Future agent ecosystems we don't have names for yet

The cost is real: each test is a real LLM call (~30 seconds, real
API spend, non-deterministic). For a 30-prompt × 4-runtime × 3-trial
harness, that's 360 LLM calls per release cycle. Run weekly: 1500
calls a week. Run on every PR: budget accordingly.

But the bugs you catch are bugs that would otherwise ship to users
silently. The trade is real spend now vs. real user-facing breakage
later.

---

## Section 6 — What COBOL got right that we forgot (300-400 words)

The deeper lesson isn't "use COBOL." It's "use the discipline COBOL
was after."

Knuth's literate programming was after the same thing: the source
should be readable to non-programmers. BDD's Given/When/Then is the
same: the test should be readable as a specification. Cucumber's
`.feature` files: the spec IS the test IS the readable English.

These were all pointing at the same insight: **for systems whose
correctness includes a human-language layer, the test must include
that layer.**

We forgot it for two decades because most systems didn't have a
human-language layer. APIs took JSON; tests sent JSON; both spoke the
same syntax. The test pyramid (unit / integration / e2e) was sufficient.

Agent-skill products bring back the human-language layer. The agent
is the parser. The user's natural-language utterance is the input.
The expected behavior is "route to the right tool." Suddenly the
1959 acceptance pattern is exactly what we need.

The methodology survives. The guarantees become empirical. The
discipline of "the spec IS the test IS the readable English" pays
off again.

---

## Section 7 — What's next (100-200 words)

- Open-source the canonical NLQ corpus + reference runners.
- Build a unified report generator across the 4 runtimes.
- Adopt formal Gherkin emission for teams using BDD tooling.
- Establish per-runtime noise-floor tracking across the ecosystem.

If you're building agent-skill products and have routing-acceptance
methodology to share, get in touch. The corpus, the runners, and the
spec are public. The pattern is generalizable.

---

## Closing line (one sentence)

> *The 60-year-old language was right; we just had to remember why.*

---

## Publish checklist

- [x] v2.5.x COBOL barrage numbers — Claude Code 30/30, OpenClaw
  26/30, Hermes 23/30 (linux-x86-host, 2026-04-28). Aggregate evidence
  committed at `harness/reports/2.5.0-fleet-aggregate-2026-04-28.md`.
- [ ] ZeroClaw barrage — pending `fleet_provider` enc2-auth
  restoration on linux-x86-host container + Pi units (pi-small/pi-large).
  Ship without ZeroClaw or wait? (3 of 4 runtimes is publishable.)
- [x] Code links pointing at the v2.5.1 / v2.5.2 squashed releases
  on `gitlab.com/argonautsystems/InvestorClaw` and
  `.../InvestorClaude` — confirmed argonautsystems-org migration.
- [ ] Run draft past one technical reviewer (cleanroom?)
- [ ] Cross-post to Hacker News, Lobsters?
- [ ] Tag InvestorClaw fleet release announcement to coincide

## Notes / cuts

- Could include a cute "what would COBOL Hopper say about LLMs"
  section but probably reaching.
- Skip the "AI agents will replace programmers" hook. Audience is
  technical; they don't need it.
- Consider a sidebar comparing Agentic COBOL to LangSmith, Weave,
  LangFuse evals — those measure output, this measures routing.
- Think about whether techbroiler.net audience leans more
  finance-engineering or pure-engineering; tone accordingly.
