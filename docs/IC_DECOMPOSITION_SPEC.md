# InvestorClaw Decomposition Spec — v2

**Status:** REVISED DRAFT — pending Codex round-2 review and operator approval
**Date:** 2026-04-25 (revision)
**Author:** Jason Perlow
**Inputs:** GRAEAE multi-provider consensus (rounds 1 and 2), Codex round-1 review, Codex round-2 tiebreak
**Trigger:** linux-x86-host conformance-test run (2026-04-25) caught the deployed system shipping bugs against an aspirational architecture that the code didn't actually implement.

---

## 0. Reframing (most important section)

**InvestorClaw is not an agentic skill. It is a Python portfolio-analysis
library that happens to be exposed via three runtime adapters.**

- The **library** (CDM 5.x / 6.x models, computation, providers, harness, the
  `investorclaw` CLI) has its own existence and its own development life.
- The **adapters** (claws-family for OpenClaw / Hermes / ZeroClaw / standalone;
  Claude Code plugin) are runtime-specific delivery mechanisms for the library.
- The agent runtimes (Claude Code, OpenClaw, etc.) are *delivery channels*,
  not the platform the software targets.

This reframing replaces the prior "we're writing the book on agentic systems
design" framing, which led to over-engineering decisions that treated
ecosystem-standard patterns (PyPI publishing, semver discipline, pip
compatible-release operators) as if they were unsuited to this domain. They
are not. The library-and-adapters pattern has 30+ years of precedent. We
apply it.

**Why this matters for the architecture:** the prior decision framework was
"choose a novel three-repo decomposition." The correct framework is "apply
the library + adapters pattern to a project that grew up monolithic." Same
destination (three repos), simpler reasoning.

---

## 1. Problem statement

The current `InvestorClaw` repository conflates the library, two adapter
surfaces, and a contract layer in one tree:

- `/SKILL.md` — claws-family adapter contract (`/portfolio` slash, OpenClaw /
  Hermes / ZeroClaw / standalone consumers)
- `/claude/skills/portfolio-analysis/SKILL.md` — Claude Code adapter contract
  (`/investorclaw:*` slash, Claude Code marketplace consumer)
- Library code (services/, models/, providers/, runtime/, commands/) at
  repository root, mixed with adapter-specific files

The 2026-04-25 conformance-test run on linux-x86-host exposed:

- **Slow drift between the two SKILL.md files** — different slash prefixes,
  different routes for same intent, different version stamps
- **Aspirational architecture vs deployed code** — a "v2.2 9-tool consolidated
  surface" was being asserted by tests and documentation but was not
  implemented by the deployed CLI; the deployed surface is the v2.1
  per-noun command surface (`holdings`, `performance`, `bonds`, etc.)
- **Internal version inconsistencies** — frontmatter v2.2.0 with body-text
  "v2.1.9" in the same SKILL.md file
- **Operational gaps** — CLI not on PATH after `/investorclaw:investorclaw-setup`
  completed; `_incomplete:*` skills shipping to user-visible surface; four
  parallel venv installs in the user's home dir from prior install attempts

**Diagnosis:** the existing monorepo treated the library and the adapters as
one thing, with no explicit boundary between them. As a result, library
changes (which happen frequently) and adapter changes (which happen
infrequently) lived in the same release train. Because the two adapters
ship to genuinely different ecosystems with different cadences, they
drifted. Contract gates added to detect drift could only see specific
known-bad patterns; they could not enforce the structural invariant that
the library should have one canonical form regardless of adapter.

**Fix shape:** decompose into three repos along the library-vs-adapter
boundary. Make the library the canonical source of truth. Treat each
adapter as a thin runtime-specific glue layer that depends on the library.

---

## 2. Architecture: library + adapters

Three layers, three repos, standard pattern.

| Layer | Repo | Responsibility |
|---|---|---|
| **Library** | `ic-engine` | Pure Python portfolio-analysis library. CDM models, computation, providers, runtime, the `investorclaw` CLI, the V13 conformance harness. Published to PyPI. Tagged semver releases. |
| **Contract** | inside `ic-engine` | Canonical agent-skill contract template (slash-prefix-parameterized SKILL.md, route table, deflection envelopes). Build-time renders to per-adapter rendered artifacts. |
| **Adapters** | `InvestorClaw`, `InvestorClaude` | Runtime-specific glue. Adapter for the claws family lives in `InvestorClaw`; Claude Code plugin lives in `InvestorClaude`. Each adapter consumes the library and the rendered contract appropriate for its runtime. |

This is the same shape as `requests` (library) + Flask/Django/aiohttp (adapters
for HTTP server frameworks), or `lxml` + various XML toolchains. The agent
runtime is the consumer ecosystem; the adapter is the glue that surfaces
the library to that ecosystem.

---

## 3. Repository structure

### `ic-engine` — Python library + canonical contract

Published on PyPI as `ic-engine`. Source on `gitlab.com/argonautsystems/ic-engine`
with mirrors to nas + github.

```
ic-engine/
├── pyproject.toml             # name="ic-engine", console_scripts: investorclaw=...:main
├── src/
│   └── ic_engine/             # package source
│       ├── __init__.py        # canonical __version__ (single source of truth)
│       ├── cli.py
│       ├── services/
│       ├── models/            # CDM 5.x / 6.x
│       ├── providers/         # yfinance, Finnhub, FRED, Polygon, Alpha Vantage
│       ├── runtime/
│       └── commands/          # actual command implementations (Python functions)
├── contract/                  # canonical agent-skill contract
│   ├── SKILL.template.md      # parameterized: {{slash_prefix}}, {{runtime_name}}, etc
│   ├── routes.toml            # canonical route table (single source of truth)
│   ├── deflection_envelopes/  # concept, market, market-news rules
│   └── render.py              # build-time renderer: template → per-adapter SKILL.md
├── harness/                   # V13 conformance barrage (tests the library)
├── conformance/               # pseudo-COBOL conformance rigs (tests adapter contracts)
├── tests/                     # unit + integration tests
└── README.md
```

### `InvestorClaw` — claws-family adapter

```
InvestorClaw/
├── pyproject.toml             # depends on ic-engine via uv
├── SKILL.md                   # rendered from ic-engine contract template (commit-time artifact)
├── SKILL.toml                 # claws-family routing surface
├── openclaw.plugin.json
├── package.json + dist/       # TypeScript wrapper for OpenClaw runtime
├── hermes/install.sh          # uv pip sync against ic-engine~=2.3
├── zeroclaw/install.sh
├── standalone/install.sh
├── README.md                  # cross-references ic-engine and InvestorClaude
└── (NO claude/ subtree)
```

### `InvestorClaude` — Claude Code plugin adapter

```
InvestorClaude/
├── .claude-plugin/
│   ├── marketplace.json       # source: "./"
│   └── plugin.json
├── skills/
│   └── portfolio-analysis/
│       └── SKILL.md           # rendered from ic-engine contract template (CI-pushed artifact)
├── commands/                  # ic-*.md slash command markdown (static)
├── bin/install-investorclaw   # standard uv-based install (see §6 for mechanism)
├── README.md                  # explains relationship to ic-engine and InvestorClaw
└── LICENSE
```

---

## 4. Dependency mechanism: per-adapter, not architectural

Both adapters depend on `ic-engine`. The *mechanism* by which each adapter
sees the library is a runtime-specific install-surface choice, not an
architectural choice.

### `InvestorClaw` (claws adapter): standard pip dependency

OpenClaw / Hermes / ZeroClaw skill installers already do `uv sync` at
install time. Adding an `ic-engine` dependency to that flow is natural —
no new failure modes, no new install ceremony.

```toml
# InvestorClaw/pyproject.toml
[project]
dependencies = [
    "ic-engine ~= 2.3",  # compatible-release: absorbs MINOR + PATCH automatically
]
```

Install scripts run:
```bash
uv pip sync  # exact reproducibility from uv.lock
# (or: uv pip install --upgrade "ic-engine~=2.3" if not using lockfile)
```

### `InvestorClaude` (Claude Code adapter): CI-mirror of library source

Claude Code marketplace consumes plugins via `git clone https://gitlab.com/...
.git` with `marketplace.json` declaring `source: "./"`. The marketplace's
expectation is "this repository is self-contained at clone time." Adding a
network-dependent pip resolution at first plugin run is a degraded UX
(rate-limit risk, network partition risk, GitLab outage risk).

Therefore: `ic-engine`'s CI on each release tag pushes the library source
into `InvestorClaude/src/ic_engine/` via `git subtree split + force-push`.
The marketplace clone gets the library source already in place; no network
dependency at first run.

```yaml
# ic-engine/.gitlab-ci.yml (excerpt)
publish-investorclaude-mirror:
  stage: publish
  needs: [test, harness, conformance]
  only:
    refs: [/^v\d/]              # only on version tags
  script:
    - git remote add investorclaude
        "https://oauth2:${INVESTORCLAUDE_DEPLOY_TOKEN}@gitlab.com/argonautsystems/InvestorClaude.git"
    - git subtree split --prefix=src/ic_engine -b _engine_for_claude
    # render Claude-prefix SKILL.md from ic-engine contract template
    - python -m ic_engine.contract.render --runtime=claude_code
        --output=/tmp/claude_skill.md
    # Combine engine subtree + rendered SKILL.md + InvestorClaude L3 artifacts
    # (see Section 7 for full sync flow)
    - ./scripts/publish-investorclaude.sh _engine_for_claude /tmp/claude_skill.md
```

This is **not** the standard library + adapter pattern; it's a marketplace-
ergonomics deviation. Justified because:
- Claude Code marketplace is the consumer ecosystem we're shipping into
- `source: "./"` self-containment is the consumer's expected contract
- A pip-fetched dependency at first plugin run is a UX regression vs git-
  cloned self-contained

The deviation is bounded to one adapter (the one that can't tolerate a
network step at install time). The other adapter uses standard pip-dep.
This is **per-adapter mechanism choice**, not architectural divergence.

### Why this is not "vendoring"

Vendoring is "we copy the dependency into our repo and forget about it."
What we're doing is: the dependency's CI publishes a known-good snapshot to
the consumer repo on every release. The consumer repo cannot fork because
CI overwrites; the dependency repo is the canonical authority; the
relationship is enforced mechanically by force-push, not by trust.

This is closer to how pre-built binaries land in Linux distribution
package mirrors than to traditional vendoring.

---

## 5. CI / CD: standard semver discipline + automated downstream tests

`ic-engine` uses strict semver:
- **MAJOR** = breaking change to public API (CLI surface, contract template,
  command name, model schema)
- **MINOR** = additive (new command, new provider, new contract clause)
- **PATCH** = bugfix only

`ic-engine` CI on tag push:
1. Runs unit tests, V13 harness, and pseudo-COBOL conformance against the
   library + rendered contracts for both adapters
2. Publishes to PyPI
3. Triggers downstream pipelines in `InvestorClaw` and `InvestorClaude` to
   run their adapter-side conformance tests against `ic-engine==<new tag>`
4. For `InvestorClaude` specifically: publishes the engine-source mirror +
   rendered Claude-prefix SKILL.md to the InvestorClaude repo (force-push)

Adapter CI on its own commits:
1. Runs adapter-side conformance against the highest-matching pinned
   `ic-engine` version
2. Catches adapter-side regressions independently of engine releases

**No auto-bump bot.** With strict semver discipline + compatible-release pins
in adapter `pyproject.toml`, adapter consumers automatically absorb safe
upgrades. Breaking changes deserve human attention.

### Contract gates (replacing the brittle "every route round-trips" gate)

For both adapters' CI:
1. **Single SKILL.md per repo.** Any second SKILL.md is a critical fail.
2. **Rendered SKILL.md diffs cleanly from `ic-engine`'s template** (the
   adapter didn't hand-edit the rendered artifact).
3. **Slash prefix in rendered SKILL.md matches the runtime target.** Claude-
   side gets `/investorclaw:*`; claws-side gets `/portfolio`. No prefix
   confusion.
4. **Version stamp matches `ic_engine.__version__`** at render time.

The "every slash route round-trips through engine CLI dispatch" assertion
from spec v1 §7 is downgraded to a smoke test, not a blocking gate (per
Codex round-1 review — brittle as primary blocker).

---

## 6. Migration plan: prototype-first, six phases

Per Codex round-1 recommendation: prove the L2 centralization in the
current monorepo BEFORE extracting any repo. The decomposition decision is
robust regardless of phase ordering, so we de-risk by validating the
template + render approach in place first.

### Phase 0 — Instrument current monorepo (rollback baseline)

- Fix the existing 2.2.0 / 2.2.1 / "v2.1.9" body-text version drift in
  place (single source of truth in `__init__.py`)
- Reconcile the v2.2 9-tool surface vs deployed v2.1 per-noun surface —
  pick one, propagate to docs, contract gates, conformance test
  expectations
- Tag as `InvestorClaw v2.2.2` — **the rollback baseline.** If any
  subsequent phase encounters a blocker, revert here.

### Phase 0.5 — Prototype contract centralization in monorepo

- Add `contract/SKILL.template.md` + `contract/routes.toml` +
  `contract/render.py` to the current monorepo
- Generate both `SKILL.md` (claws prefix) and `claude/skills/portfolio-analysis/SKILL.md`
  (Claude prefix) from the template
- Run the pseudo-COBOL conformance rig against both rendered outputs from
  a fresh host (linux-x86-host or mac-arm-host, not mac-dev-host due to context contamination)
- **Commit the conformance result as a baseline artifact** at
  `contract/conformance-baseline-<YYYY-MM-DD>.txt` (per Codex round-2).
  This is the rollback signal: if Phase 1 or 2 conformance diverges from
  the baseline, you know exactly where it broke. A passing conformance
  run that isn't recorded is half a verification.
- **If conformance against the baseline holds:** the L2 centralization is
  proven. Proceed to Phase 1.
- **If conformance fails or diverges from the baseline at any subsequent
  phase:** the spec's core assumption is wrong. Revisit.

### Phase 1 — Extract `ic-engine` (library extraction)

- `git init gitlab.com/argonautsystems/ic-engine` with nas + github mirrors
- `git subtree split --prefix=<library paths>` to preserve history
- Add `pyproject.toml` with `name="ic-engine"`, `console_scripts: investorclaw`
- Move `contract/` and `harness/` and `conformance/` into ic-engine
- Publish to PyPI as `ic-engine v2.3.0`
- Verify `uv pip install ic-engine` produces a working `investorclaw` CLI
  on a fresh host
- **InvestorClaw monorepo is unchanged at this point** — engine is dual-
  located (in monorepo subtree AND in ic-engine repo) until Phase 2 cuts
  over.

### Phase 2 — Slim `InvestorClaw` to claws-family adapter

- Replace the in-tree library subtree with `ic-engine~=2.3` dependency in
  `pyproject.toml`
- Update `hermes/install.sh`, `zeroclaw/install.sh`, `standalone/install.sh`
  to do `uv pip sync` (which pulls ic-engine via the new dependency)
- The root `SKILL.md` is now a build-artifact rendered from `ic-engine`'s
  template (committed to the InvestorClaw repo for marketplace
  consumption)
- Test all four install paths (OpenClaw / Hermes / ZeroClaw / standalone)
  end-to-end with the conformance rig
- Tag as `InvestorClaw v2.3.0` (claws-adapter version, distinct from
  ic-engine version — see §7)

### Phase 3 — Create `InvestorClaude` (Claude Code adapter)

- `git init gitlab.com/argonautsystems/InvestorClaude` with nas + github mirrors
- `git subtree split --prefix=claude` from current InvestorClaw to preserve
  history of the Claude-side files
- Add `bin/install-investorclaw` doing `uv pip sync` for non-engine deps
  (engine source is mirrored in by `ic-engine` CI; no pip install of engine
  needed at plugin first-run)
- Move the pseudo-COBOL conformance rig to `ic-engine/conformance/` (where
  it lives canonically) and configure InvestorClaude CI to run it against
  its own rendered SKILL.md
- Wire CI for the four contract gates (§5)
- Submit to Claude Code marketplace under new source URL
  `gitlab.com/argonautsystems/InvestorClaude.git`
- **Marketplace migration:** existing InvestorClaw-on-Claude-Code users
  must `/plugin marketplace remove investorclaw` and re-add from the new
  URL. Document in release notes.

### Phase 4 — Deprecate monorepo `claude/` subtree

- Add deprecation notice in `InvestorClaw/claude/README.md` pointing to
  InvestorClaude
- Leave subtree in place for one InvestorClaw release to allow user
  migration
- Remove in `InvestorClaw v2.4.0` cleanup

### Phase 5 — Adopt build-time SKILL.md render across both adapters

- Both adapter repos ship pre-rendered SKILL.md as a CI artifact (NOT
  rendered at install time)
- Removes any install-time correctness dependency on the engine being
  reachable for the render step
- Removes any adapter-side "edit the rendered SKILL.md by hand" risk
  (contract gate #2 catches it)
- This is the change that closes the original drift bug class.

### Phase 6 — Cleanup + observability

- Remove the temporary subtree-sync between monorepo and ic-engine (the
  monorepo subtree is removed entirely once Phase 2 cuts over)
- Remove the routing-rule parity contract gate from the original
  InvestorClaw (it asserted parity between two SKILL.md files in the same
  repo; that's no longer the topology)
- Update fleet documentation (`~/.claude/CLAUDE.md`, MNEMOS memories) to
  reflect three-repo architecture

---

## 7. Versioning: how patches flow

Three repos, three semver lines, with explicit relationships.

### `ic-engine` semver

Pure library semver. `v2.3.0`, `v2.4.0`, `v3.0.0`, etc.
- MAJOR = breaking API change (CLI surface, contract template, command name)
- MINOR = additive (new provider, new command, new contract clause)
- PATCH = bugfix

### Adapter semver: independent, with engine compatibility range

Each adapter has its own version line, with an explicit
`ic-engine>=X.Y, <Z` compatibility range declared in `pyproject.toml`.

`InvestorClaw v2.3.0` means: this is the `claws-adapter` release that
ships against `ic-engine ~= 2.3`. If we fix a Hermes-installer-only bug,
we ship `InvestorClaw v2.3.1` without changing `ic-engine` at all.

`InvestorClaude v2.3.0` means: this is the `claude-adapter` release that
ships against `ic-engine ~= 2.3`. If we fix a slash-command-markdown
typo, we ship `InvestorClaude v2.3.1` without changing `ic-engine` or
`InvestorClaw`.

**Independent patches are now structurally supported.**

### When does the engine bump trigger adapter bumps?

- **MAJOR engine bump:** breaking API change. Adapters MUST bump their
  compatibility range and re-test. Triggers adapter bumps.
- **MINOR engine bump:** additive change (e.g. new provider). Adapters
  MAY bump to expose the new functionality but are not forced to. Their
  existing compatibility range (`~= 2.3`) automatically absorbs the new
  minor version.
- **PATCH engine bump:** bugfix. No adapter action required. Fresh
  adapter installs automatically pull the new patch via the compatibility
  pin.

### When does an adapter bump trigger anything?

- **MAJOR adapter bump:** breaking adapter-surface change (e.g. slash
  prefix change, marketplace.json schema change). Affects only consumers
  of THAT adapter.
- **MINOR / PATCH adapter bump:** adapter-internal change. No upstream
  effect.

This is the same model that any Python library with multiple ecosystem
adapters uses. Independent patches in every direction.

---

## 8. Failure-mode analysis

**Closed by this architecture:**
- Two-SKILL.md drift (one canonical template, two rendered outputs)
- Slash-prefix divergence (prefix is a render-time variable in the template)
- Version-stamp mismatch (version comes from `ic_engine.__version__` at
  render time; matches via contract gate #4)
- Aspirational-vs-deployed surface drift (the contract template lives with
  the implementation in `ic-engine`; if the template asserts a route, the
  engine implements it, validated by contract gate #2 + smoke tests)

**Introduced:**
- **Engine pin skew across adapters.** `InvestorClaw` could pin `ic-engine
  ~= 2.3` while `InvestorClaude` pins `~= 2.4`. Behavior diverges across
  runtimes. *Mitigation:* keep adapter pins in lockstep as policy, with
  contract gate #4 (version stamp consistency) catching mismatch at
  install time.
- **PyPI / GitLab availability dependency for claws adapter.** `uv pip sync`
  needs network. *Mitigation:* low probability for a fleet that already
  requires network for skill installation; document fallback `git+https://
  gitlab.com/argonautsystems/ic-engine.git@v2.3.0` URL.
- **InvestorClaude force-push semantics.** Direct PRs against
  InvestorClaude get destroyed on next CI publish. *Mitigation:* loud
  README-as-policy ("DO NOT PR DIRECTLY"); issue tracker on InvestorClaude
  redirects to upstream repos. **AND** (per Codex round-2) an explicit CI
  enforcement guard in InvestorClaude that aborts on any modified file
  under `src/ic_engine/` whose commit author is not the `ic-engine` CI
  pipeline. README warning alone is necessary but not sufficient — the
  CI check is the structural enforcement.
- **Three-repo cognitive load for solo dev.** Most features touch only
  `ic-engine`. Adapter changes are rare once stable. The whole point of
  the architecture is that L1 / L3 change at different rates; the
  cognitive load is bounded by that asymmetry.

**Net assessment:** the new failure modes are **lower-severity, lower-
probability, and observable at install / CI time** rather than silent at
runtime. Strict improvement in observability over the current architecture,
where drift produces silent agent misbehavior with no error message.

---

## 9. The pseudo-COBOL conformance rig becomes house style

The COBOL test rig that caught today's bugs is being adopted as the house
format for all conformance tests, not just routing.

Properties demonstrated:
- **Anti-fabrication armor:** rigid 88-conditions, level-numbered records,
  PIC-shape declarations make "make stuff up" structurally visible
- **Cross-LLM legibility:** the format survives translation across model
  families (Gemini, Grok, Claude, Llama equivalents)
- **Honesty meta-rules embedded in DATA DIVISION** load reliably across
  sessions
- **Override-token machinery is structurally distinguishable from policy
  text** (after the v2 fix in this session)

Lives in `ic-engine/conformance/` as the canonical home. Each adapter's CI
runs the rigs against its rendered SKILL.md.

Domains worth porting to:
- Provider-conformance (does the FRED provider return the schema we
  expect?)
- Plugin-install conformance (does the marketplace install path produce
  a working plugin?)
- Contract-gate self-tests (does the gate detect what it's supposed to
  detect?)

---

## 10. Open questions for Codex round-2 review

Items the spec resolves but flags for second-pass examination:

1. **PyPI publish vs. git+ URL only.** Spec defaults to PyPI. Adds release
   ceremony but solves anonymous-fetch availability. Worth Codex sanity
   check — solo-dev cost of PyPI release ceremony vs. value.

2. **Should `ic-engine`'s contract template render at engine release time
   (and the artifact gets shipped to adapters) or at adapter release time?**
   Spec § 6 Phase 5 picks adapter release time as the artifact-commit
   point. Build-time at engine vs. adapter is a real choice.

3. **Marketplace migration UX for InvestorClaude transition.** Phase 3
   requires existing users to `/plugin marketplace remove + add` to switch
   from InvestorClaw-bundled-Claude-plugin to the new InvestorClaude repo.
   Best practices for Claude Code plugin URL migration are not well-
   documented. Codex may have ecosystem-pattern signal.

4. **OpenClaw skill registration timing.** OpenClaw skills register at
   `uv sync` install time. Confirming the new pip-dep flow doesn't break
   existing OpenClaw skill registration semantics.

5. **CI cost on GitLab free tier.** Multi-project pipelines + force-push
   permissions + downstream conformance tests use pipeline minutes. Verify
   we don't exhaust the free-tier budget.

6. **Engine schema evolution.** The contract template lives with the
   engine, so engine MAJOR bumps require coordinated adapter bumps. Should
   there be a "contract-schema" version separate from the `ic-engine`
   library version, so that contract changes don't always force library
   MAJOR bumps?

---

## 11. Decision summary

| Decision | Choice | Why |
|---|---|---|
| Decompose? | Yes — three repos | Library + adapters is the standard pattern; current monorepo conflates layers |
| Library repo | `ic-engine` on PyPI | Standard Python ecosystem distribution |
| Claws adapter mechanism | `uv pip sync` against `ic-engine ~= 2.3` | OpenClaw / Hermes / ZeroClaw installers already do uv sync; no new failure modes |
| Claude Code adapter mechanism | CI-mirror engine source from `ic-engine` | Marketplace `source: "./"` self-containment expectation |
| Contract template location | `ic-engine/contract/` | Single source of truth for the L2 contract |
| Render time | Engine release time → committed to adapter repos as artifacts | Build-time per Codex round-1; immutable, reviewable, no install-time correctness dependency |
| Versioning | Independent semver per repo, with engine compat range in adapters | Standard Python ecosystem pattern; supports independent patches |
| Migration sequencing | Phase 0/0.5 prototype → engine extract → slim claws → create Claude → deprecate → cleanup | Per Codex round-1, prototype centralization in monorepo BEFORE splitting |
| Conformance test format | pseudo-COBOL, lives in `ic-engine/conformance/` | Demonstrated effectiveness across LLM families |

---

## 12. References

- GRAEAE consultation 2026-04-25 round 1 (eight providers)
- GRAEAE consultation 2026-04-25 round 2 (option-comparison)
- Codex round-1 review of spec v1 (recommended prototype-first, build-time
  SKILL.md, demoted brittle gates, surfaced uv pip sync vs install)
- Codex round-2 review of spec v1 H′ vs H″ (broke tie toward H″)
- Operator reframing 2026-04-25: "this is not an agentic skill, this is
  actual software now that happens to run in an agent" — the highest-
  leverage observation in this thread
- Conformance test result that triggered this work:
  `/Users/user/conformance-test-result-linux-x86-host-2026-04-25.md`
- Prior architecture decisions: `docs/ARCHITECTURE_DECISIONS.md`
- Fleet conventions: nas = source of truth, gitlab = CI + install
  surface, github = mirror

---

**Status:** AWAITING CODEX ROUND-2 REVIEW.

Codex: please examine §0 (reframing — does treating this as library +
adapters change your prior recommendation?), §4 (per-adapter mechanism
choice — is asymmetric pip-vs-CI-mirror sound?), §6 (migration sequencing
— Phase 0.5 prototype is new), §7 (independent semver per repo with
compat range), and §10 open questions. Identify gaps the reframing
introduces, alternative architectures the new framing makes available
that prior framing obscured, and whether the mechanism asymmetry
(claws=pip, Claude=CI-mirror) is justified or should normalize.
