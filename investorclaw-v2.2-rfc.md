# RFC: InvestorClaw v2.2 — SKILL.toml tool consolidation + routing hygiene

**Status:** Revised draft — GRAEAE-consensus-informed.
**Target release:** v2.2.0
**Base commit:** `7821165` (v2.1.9 + SKILL.toml routing extensions)
**Author:** Jason Perlow
**Date drafted:** 2026-04-24
**Revision log:**
- r2.3 (2026-04-24 23:10 UTC): Applied ordered fixes 1-11. Changes: (1) kept `portfolio_market` unified with default `section=news` and added hard NL negative examples for market/concept deflection vs news routing; (2) removed NewsAPI from all market-wide `portfolio_market` routing chains while preserving it for portfolio-scoped `portfolio_view --section=news`; (3) replaced stale external `--mode` examples with `--section` while preserving the legacy internal `--mode` collision discussion; (4) corrected appendix `MODE_DISPATCH` sketch to real consolidated wrapper keys with no top-level `analyze`; (5) added v2.4+ asset-class ownership contract for held positions vs market-wide news; (6) corrected treasury/free-first routing and marked forex/GDELT empirical verification fallback; (7) added combined canonical-JSON equivalence gate for news/concept/market in one pytest invocation; (8) added setup-wizard existing-key detection pass; (9) corrected rollout tool count to 9; (10) removed `portfolio_futures` from §3.1 future asset-class list; (11) tightened non-goal wording around `portfolio_bonds`.
- r0 (2026-04-24 16:07 UTC): Initial draft. 9 tools, MPT standalone, target absorbed identity.
- r1 (2026-04-24 17:40 UTC): Revised after Opus-4.7 validation + GRAEAE consensus (consultation `adf242e9-cd22-41a2-ba63-3e236f04d897`, 3/3 complete muses unanimous on MPT-fold, 2/3 on identity-split). Tool count 9 → 8. `portfolio_mpt` folded into `portfolio_compute` with `mode=optimize-sharpe|optimize-minvol|optimize-blacklitterman`. Identity moved from `portfolio_target` to `portfolio_config`. Rejected alternatives expanded.
- r2 (2026-04-24 18:30 UTC): Applied codex-r3 findings + second GRAEAE consensus (consultation `a5ce2d7f-55db-4d12-a736-2a129fa418d9`, 8/8 muses including Claude responding). Changes: (1) fixed `MODE_DISPATCH["analyze"]` regression trap; (2) `snapshot_id` REQUIRED in staging envelope; (3) byte-equivalence respec'd as canonical-JSON equivalence; (4) `portfolio_bonds` extracted as standalone; (5) `portfolio_fixed_income` extracted as standalone; (6) wrapper arg renamed `--mode` → `--section`; (7) §3.6 cross-phase intents demoted to future; (8) §3.5 asymmetric CLI-vs-tools kept + CI sync-test; (9) §6.2 narration gate rewritten against real `portfolio_complete.py`; (10) asset-class-extensibility contract documented. Tool count 8 → 10.
- r2.1 (2026-04-24 18:55 UTC): User caught that splitting bonds (descriptive) from fixed_income (strategy) was conflating asset-class separation with verb separation — both operate on the same asset class. Merged `portfolio_fixed_income` back into `portfolio_bonds` with `section=analysis|strategy` args. Name stays `portfolio_bonds` because that's how consumers query. Asset-class-extensibility contract clarified: one tool per asset class, not one tool per (asset-class × verb) pair. Tool count 10 → 9.
- r2.2 (2026-04-24 22:30 UTC): Added news surface architecture (§3.7) after Yahoo Finance reference alignment. News splits along ownership axis: `portfolio_view --section=news` = portfolio-scoped (per-ticker for held positions); `portfolio_market --section=news --topic=X` = market-wide (4 Finnhub-native categories). Comprehensive provider matrix, NL-trigger vocabulary, topic×provider routing chain, and hierarchy organization added. Core 4 topics (general/forex/crypto/merger) ship functional in v2.2 using only existing provider abstraction. Extended topics (macro/earnings/ipo/sector/movers/insider) deferred to v2.3. Asset-class topics (filings/treasury/commodities/metals) and asset-class standalone tools (portfolio_fx/metals/commodities/crypto/derivatives) deferred to v2.4+. New §9 Roadmap codifies the phase plan. Tool count stays at 9 (v2.2 expansion is within portfolio_market, not a new tool).

---

## 1. Context

Today's cross-runtime NL-pilot evidence (2026-04-24) shows a routing-quality gap across agent runtimes against an identical skill (InvestorClaw) and identical LLM (Gemini-flash-latest):

| Runtime | Score | Notes |
|---|---|---|
| OpenClaw | 10/10 | Plugin-as-code model; subcommands are first-class tools |
| ZeroClaw master | 4–7/10 | `[[tools]]` manifest works but regressed after expanding 17→19 tools with longer descriptions |
| Hermes Agent | 3–5/10 | Skills are advisory prompt text, not native `tools[]` entries |
| Claude Code | 10/10 | Plugin + skills path; native enforcement |

Codex correlation analysis (2026-04-24) confirmed:
- ZeroClaw's regression is likely driven by **tool-description overlap + paragraph-length copy** (`SKILL.toml:146–260`) once the manifest grew past ~17 tools.
- Hermes drift is **runtime-level** (skills live in the system prompt, not the tool manifest) — not fully fixable at the skill layer.
- OpenClaw's lead comes from **first-class subcommand registration** via `openclaw.plugin.json`.

Also surfaced: `SKILL.md:89–108` routes "full picture" to `/portfolio complete`, but `runtime/router.py:41–152` has no `complete` entry, and `SKILL.toml` has no `portfolio_complete` tool. Dangling contract.

## 2. Problem statement

**v2.2 is a presentation-layer change, not a code refactor.** The underlying deterministic Python system (`commands/*.py`, `runtime/router.py` dispatch, `ic_result` envelope contract, consultation policy) works correctly. This RFC does not touch that layer.

The problem we are solving is twofold, both at the human/LLM-facing surface:

1. **End-user cognitive load.** InvestorClaw advertises ~23 user-facing commands across `SKILL.md`, `COMMANDS.md`, and the `/portfolio *` slash menu. A new user reading that list has to hold 23 separate mental models to pick the right one. Workflow-aligned verb grouping (observe / compute / aspire / simulate / context) reduces the mental model to 5 workflow tools + 1 bonds standalone + 3 utility tools = 9.

2. **LLM tool-selection routing.** Empirical cross-runtime pilot data (2026-04-24) shows LLM routing quality degrades as the tool manifest grows past ~15 entries. ZeroClaw + Gemini regressed from 7/10 to 4/10 when `SKILL.toml` expanded from 17 tools to 19 with longer NL-trigger descriptions. OpenClaw holds at 10/10 because its plugin registration mechanism is different — the surface size hits OpenClaw less sharply — but even OpenClaw will benefit from cleaner naming.

Supporting observations that reinforce the surface-pressure issue (not independent problems):

- **Overlap** — `portfolio_synthesize`, `portfolio_analysis`, and `portfolio_complete` all target "run the full pipeline," differentiated only by scope. Users AND models see three names for overlapping concepts. Separately, `portfolio_bonds` and `portfolio_fixed_income` in v2.1.9 duplicate each other on the same asset class (merged in v2.2 under `portfolio_bonds` with section args).
- **Verbosity** — several v2.1.9 descriptions exceed 300 characters with embedded "ALWAYS do X, do NOT do Y" clauses. These were added to shore up LLM routing but dilute both the match signal and the human reading experience.
- **Dangling contracts** — `portfolio_complete` advertised in `SKILL.md` but unrouted in `router.py` COMMANDS dict. Confusing for users who try to run it, and for LLMs encountering a semantic inconsistency.

### Explicit non-motivations

- **NOT a code quality issue.** The Python command scripts are clean, tested (607/607 passing), and doing their jobs correctly.
- **NOT a maintainability issue.** `runtime/router.py` is ~450 lines and easy to modify; adding commands has been straightforward.
- **NOT a correctness issue.** Every `ic_result` envelope emitted today is accurate; the data layer is sound.
- **NOT a performance issue.** Command dispatch cost is negligible vs. the actual analysis work.

Consolidation is **presentation-only**. Every current script stays in place. Every current command-line invocation keeps working via legacy aliases (see §3.3). The CSV-strip contract, tier-3 consultation injection, ic_result envelope, and auto-bootstrap flow all remain byte-for-byte identical to v2.1.9.

## 3. Design principles + proposal

### 3.0 Design principles (hard constraints)

#### 3.0.1 Output fidelity is non-negotiable

**Consolidation MUST NOT lose data or truncate output.** Every byte of information the current 19-tool surface produces for a given user intent must remain accessible in v2.2. If a consolidated tool's output would exceed a safe per-response budget (proposed: 32 KB payload; 64 KB absolute ceiling including envelope overhead), the tool paginates via a staging contract rather than trimming.

**Stronger invariant: per-section output is canonically-JSON-equivalent to the current per-script output.** Specifically:

> Define canonical equivalence: parse both outputs as JSON (where applicable), sort all dict keys recursively, strip volatile fields (`timestamp`, `ic_result.duration_ms`, process IDs, random seeds, absolute paths), normalize whitespace. Two outputs are equivalent iff their canonical forms are byte-identical.

`portfolio_view --section=holdings` must be canonically equivalent to `investorclaw holdings`. `portfolio_compute --section=synthesize` must be canonically equivalent to `investorclaw synthesize`. Etc. The consolidated tool is a *dispatcher*, not a transformer — it selects which underlying script to run, runs it, and returns the script's output unchanged.

Why canonical-JSON equivalence, not raw bytes: Python `json.dumps` dict-iteration order is not guaranteed stable across invocations, and wrapper-vs-direct invocations can serialize in different orders even when producing semantically identical data. Raw-byte comparison would produce false-positive failures on a correct implementation. The canonical-form rule catches real regressions while ignoring serialization noise.

**Tools do not narrate; the LLM does.** Every consolidated tool returns a raw `ic_result` envelope with structured fields matching today's contract. No tool pre-summarizes, prose-wraps, or selectively filters the underlying data. When a user asks something that spans multiple modes (e.g., "give me the full picture"), the LLM chains multiple tool calls, reads all the envelopes, and composes the natural-language response. This is the division of labor:

- **Tool layer:** deterministic data production. Identical to v2.1.x.
- **LLM layer:** natural-language composition across one or more tool responses. Uses staging for large single-mode outputs; uses sequential multi-tool calls for multi-mode coverage.

This invariant makes v2.2 safely implementable: if the test suite proves canonical-JSON equivalence between `investorclaw holdings` and `portfolio_view --section=holdings` (and analogously for every other section mapping), the consolidation has not broken anything the deterministic system was doing.

#### 3.0.2 Staging contract

Any consolidated tool MAY return a **staged response** when it determines output would exceed the budget. Contract:

- Each stage is a **complete, self-describing ic_result envelope**. A stage is independently parseable.
- Stage envelope gains four REQUIRED fields (all MUST be present, not optional):
  - `"stage": { "n": 1, "of": 3 }` — current / total
  - `"stage_key": "holdings-core"` — stable identifier for what's in this stage. Format: `<tool>:<section>:<stage-name>` (e.g., `view:holdings:accounts-1`, `compute:optimize-sharpe:frontier`). Deterministic for a given (tool, section, input, snapshot_id).
  - `"snapshot_id": "sha256:abc123..."` — **REQUIRED**. SHA-256 of the canonical input state (resolved holdings file + any persisted target/identity state). Pins the staged response series to a specific snapshot of user state. If the user's portfolio or target changes between stage N and stage N+1, the new request receives a new `snapshot_id` and the client MUST treat the earlier stages as stale.
  - `"next_stage_args": { "stage": 2, "snapshot_id": "sha256:abc123..." }` — args the agent should pass to retrieve the next stage. Must include the `snapshot_id` so the dispatcher can reject stale continuations. Empty/null when `n == of`.
- The tool accepts `--stage <N>` and `--snapshot-id <hash>` CLI flags. Default stage = `1`; default snapshot_id = compute fresh. When agent requests stage N with a `snapshot_id` that no longer matches current state, the dispatcher returns `ic_result.exit_code=2` and `"stale_snapshot": true`.
- Consolidated tools that always fit in one response (e.g. `portfolio_market`'s decline envelope ~500 bytes) simply emit a single stage with `"stage": { "n": 1, "of": 1 }`. No additional retrieval needed, but the four fields are still present.

#### 3.0.3 When staging kicks in (concrete)

Empirical size observations from today's pilot runs on the 335-position test portfolio:

| Current tool | Typical output | Staging likely? |
|---|---|---|
| `fetch_holdings.py` | 8–15 KB | sometimes (large accounts) |
| `analyze_performance_polars.py` | 3–5 KB | no |
| `bond_analyzer.py` | 3–8 KB | no |
| `fetch_analyst_recommendations_parallel.py` | 10–25 KB | yes for >50 positions |
| `fetch_portfolio_news.py` | 5–20 KB | yes for active news windows |
| `portfolio_analyzer.py` (full synthesis) | 20–40 KB | **always — default to stages** |
| `portfolio_complete.py` (8-stage pipeline) | 40–80 KB | **always — one ic_result per pipeline stage** |

So: consolidation doesn't force staging on small tools; it just makes staging a first-class capability available to any tool whose natural output is big. The synthesis + complete tools are the first-class citizens that ALWAYS stage — each of their internal pipeline steps becomes a stage externally.

#### 3.0.4 Agent orchestration note

The consolidated-tool-with-stages pattern is strictly better for model reasoning than the current multi-tool pattern:

- **Today:** model picks one of 19 overlapping tools → hopefully picks the right one → single response (may be large and truncate).
- **v2.2:** model picks one of ~9 clearly-named tools → response may come in stages → model accumulates stages in its working context across turns → synthesizes at the end.

Multi-turn stage retrieval is exactly what tool-calling models are good at. The orchestration cost is lower than the current 19-tool routing cost.

### 3.1 Consolidation mapping

Reduce 19 tools to **9 tools, 6 of them section-dispatched.**

**Total: 9 tools** (down from 19 in v2.1.9). Workflow 5 + 1 asset-class standalone (bonds) + 3 utilities.

**Workflow 5** (phase-verb aligned — observe → compute → aspire → simulate → context):

| Consolidated tool | Replaces | `section` values | Output shape |
|---|---|---|---|
| `portfolio_view` | holdings, performance, analyst, news (portfolio-scoped), dashboard-deferral | `holdings \| performance \| analyst \| news \| dashboard` | Section-keyed JSON envelope; `news` fetches per-ticker news for HELD positions only (existing `fetch_portfolio_news.py` behavior); `dashboard` returns the canonical deferral envelope |
| `portfolio_compute` | synthesize, optimize (Sharpe/min-vol/Black-Litterman) | `synthesize \| optimize-sharpe \| optimize-minvol \| optimize-blacklitterman` | Narrative synthesis OR numerical MPT weights + efficient-frontier pointer |
| `portfolio_target` | session (allocation), update-identity-partial (drift only) | `allocation \| drift` | Target-state JSON; persisted to `~/.investorclaw/target.json` for cross-call reference |
| `portfolio_scenario` | scenario, rebalance_tax, stress-test | `rebalance \| stress \| tax-aware` | Scenario envelope (trade trees or stressed allocations); reads persisted target state |
| `portfolio_market` | market-wide deflection, concept deflection, **+ NEW: market-wide news** | `news \| concept \| market` | Default section = `news`. **`news` (v2.2, functional):** market-wide news across 4 categories via `--topic=general\|forex\|crypto\|merger`. See §3.7 for full provider routing. Free/keyless endpoints are prioritized over quota-gated fallbacks. **`concept`, `market`:** canonical decline envelope, reason-coded (unchanged from r2.1) |

**Asset-class standalone 1** (one tool per asset class, not per verb):

| Tool | `section` values | Underlying scripts | Notes |
|---|---|---|---|
| `portfolio_bonds` | `analysis \| strategy` | analysis → `bond_analyzer.py`; strategy → `fixed_income_analysis.py` | Default section = `analysis` (the common consumer query). `strategy` surfaces laddering, duration matching, credit-quality tiering, income optimization. Tool name uses "bonds" because that's how consumers query — "show my bonds," "analyze my bonds" — even though the underlying domain covers the broader fixed-income umbrella (TIPS, MBS, preferreds when those land). |

**Why one asset-class tool, not two.** Earlier r2 drafts split this into `portfolio_bonds` (descriptive) and `portfolio_fixed_income` (strategy). That split confused asset-class separation with verb separation — bond_analyzer and fixed_income_analysis operate on the same asset class, they just DO different things with it. The proper split here is by `section` (analysis vs strategy) inside one asset-class tool, not by tool.

**Asset-class extensibility contract.** The standalone-per-asset-class pattern is the pattern for future asset types:

- `portfolio_crypto` — cryptocurrency holdings. Custody mode (exchange vs self-custody), tax-lot tracking with high-frequency cost basis.
- `portfolio_commodities` — physical commodity exposure. Contango/backwardation awareness.
- `portfolio_precious_metals` — physical vs paper gold/silver, storage costs.

Each asset class has a distinct domain model — futures expiries don't apply to equities, crypto cost-basis lot tracking doesn't apply to bonds, physical commodity storage doesn't apply to anything else. When those land, each gets its own tool with its own `section` list, not a mode of a generic catch-all. The v2.2 pattern is:

> **Generic workflow tools (view/compute/target/scenario/market) for cross-cutting portfolio operations that work across all asset classes. One asset-class-specific standalone per distinct domain model, with `section` args for the different verbs on that asset class.**

Tool count grows linearly with asset classes, not with (asset_class × verb) combinations. v2.3 might be 10 tools (add crypto); v2.4 might be 12 (add futures + commodities). The LLM surface stays clean because each tool has a clean single domain purpose, even as the number of tools grows.

**Utility 3** (not part of the workflow; no phase affiliation):

| Tool | Replaces | Purpose |
|---|---|---|
| `portfolio_config` | setup, update-identity (risk profile/age/horizon), guardrails | One-time plumbing + persona. Sections: `setup \| identity \| guardrails` |
| `portfolio_report` | report, eod-report, export | Export CSV/XLSX/PDF. No section arg; file-format inferred from args |
| `portfolio_lookup` | lookup | Ticker/account drill-in. Flags: `--symbol TICKER`, `--accounts` |

**Notable changes from r1:**
- **Wrapper arg is now `--section`, not `--mode`.** GRAEAE-r2 consensus (5 of 7 muses) selected `--section` to avoid collision with the existing `--mode` args in `portfolio_analyzer.py:76-85`, `fixed_income_analysis.py:31-39`, and `optimize.py:87-95`. `--mode` is stripped at the wrapper layer before dispatch if an underlying script also uses `--mode`; `--section` is the clean external contract.
- **`portfolio_bonds` extracted** from `portfolio_view` per user decision — bond analysis has a materially different schema.
- **Fixed-income strategy folded into `portfolio_bonds --section=strategy`** (r2.1) — originally extracted in r2 as its own `portfolio_fixed_income` tool per GRAEAE 4-3, then merged back into `portfolio_bonds` after user caught that the split conflated asset-class separation with verb separation. See r2.1 revision-log entry for full rationale.
- **v2.1 `analyze → performance` alias preserved.** The consolidated `portfolio_view` tool name does NOT collide with `analyze`; r1's appendix `MODE_DISPATCH["analyze"]` entry was removed. Legacy `investorclaw analyze` continues to dispatch to `analyze_performance_polars.py` as in v2.1.

### 3.2 Description discipline

- First sentence ≤ 100 characters.
- Must name at least one canonical NL trigger phrase from `references/presentation-nl-query-routing.md`.
- No "ALWAYS" / "do NOT" imperatives — move those to the `prompts` array in `[skill]` where they're injected as system-prompt context, not per-tool noise.

Example:

```toml
# Before (SKILL.toml v2.1.9, 358 chars across portfolio_holdings)
description = "Show the user's own portfolio holdings — live prices, quantities, market values, allocation percentages, sector breakdown. Use for 'show me my holdings', 'what do I own?', 'list my positions', 'what's in my portfolio?', 'what's my total portfolio value?'. ALWAYS prefer this over memory lookups or fabricating position data."

# After (v2.2, 96 chars for portfolio_view)
[[tools]]
name = "portfolio_view"
description = "Observe the user's portfolio. Use for 'show my holdings', 'how's performance?', 'portfolio news'."
kind = "shell"
command = "investorclaw view --section {{section}}"
args = { section = "holdings|performance|analyst|news|dashboard (default: holdings)" }
```

`[skill]` prompt guidance carries the hard routing negatives that should not be repeated in per-tool descriptions:

```toml
prompts = [
  "'price of NVDA' routes to portfolio_market --section=market (deflection, not news).",
  "'what is YTM?' routes to portfolio_market --section=concept (deflection, not news).",
  "'crypto news' routes to portfolio_market --section=news --topic=crypto (functional).",
  "'M&A news' routes to portfolio_market --section=news --topic=merger (functional).",
]
```

### 3.3 Router.py changes

`runtime/router.py` grows a dispatch layer:

- New `MODE_DISPATCH: dict[str, dict[str, str]]` mapping consolidated tool → mode → current script. Example: `MODE_DISPATCH["view"] = {"holdings": "fetch_holdings.py", "performance": "analyze_performance_polars.py", ...}`.
- `resolve_script()` gains a `mode` param. When absent on a consolidated tool, default to the lowest-surprise mode (e.g. `portfolio_view` default = `holdings`; `portfolio_compute` default = `synthesize`; `portfolio_scenario` default = `rebalance`). Invalid mode → hard-fail with `ic_result.exit_code=1` and an `allowed_modes` list in the envelope (per codex round-1 edge-case review).
- Legacy per-subcommand keys in `COMMANDS` stay as **permanent aliases** pointing at `<consolidated>:<mode>` so existing `investorclaw holdings` / `investorclaw performance` / `investorclaw optimize sharpe` CLI calls keep working. **The deterministic CLI surface is stable; v2.2 is a presentation-layer addition, not a removal.** See §8 for the explicit alias-longevity decision.
- **`analysis` and `complete` handling:** these retire as *advertised* tools in the SKILL manifests but the CLI commands stay permanent. `investorclaw analysis` and `investorclaw complete` continue to work as they do today (same ic_result envelopes, same output shape). What changes is only that they no longer appear as distinct `[[tools]]` entries in `SKILL.toml` — LLMs compose their semantics via sequential `view` + `compute` calls. Users typing at the CLI see no difference.
- **CSV-strip preservation:** the current contract that only `holdings` accepts a positional CSV argument (enforced by `_strip_csv_first_arg` in `runtime/router.py:353-401`) is preserved. The strip happens BEFORE mode dispatch resolution. Mode-dispatched scripts do not receive CSV positional args unless the resolved mode is `view:holdings`.
- **Tier-3 consultation injection:** `consultation_policy` evaluation targets the resolved subcommand (the downstream script), not the consolidated wrapper. Order: user args → CSV strip → mode dispatch → tier-3 injection.

### 3.4 Shell-bypass de-training

`zeroclaw/SKILL.md` currently teaches raw `pip3 install` + `python3 commands/*.py` flows (`zeroclaw/SKILL.md:42–61,74–174`). Codex flagged this as training the agent to bypass the skill. v2.2 rewrites this file to use the canonical `investorclaw <subcommand>` CLI only — same as the root `SKILL.md`.

### 3.5 Dangling-contract fix (`analysis` + `complete`)

Current state: `SKILL.md:89-108` says `/portfolio analysis` is multi-factor synthesis and `/portfolio complete` is the full 8-stage pipeline. `SKILL.toml:176-180` contradicts by making `portfolio_synthesize` the "full picture" tool. `runtime/router.py:41-152` has no `complete` entry at all. Three layers disagree.

v2.2 resolution: **retire both `analysis` and `complete` as distinct tools.** They become orchestration patterns the agent composes via sequential `portfolio_view` + `portfolio_compute` calls, exploiting the staging contract to accumulate stages across turns.

Backward compat:
- `investorclaw analysis` → continues to work exactly as today. No deprecation notice. Underlying `portfolio_analyzer.py` is unchanged. The script IS the multi-factor synthesis; we are NOT breaking it.
- `investorclaw complete` → continues to work exactly as today. `portfolio_complete.py` (the 8-stage internal orchestrator) is unchanged.
- **LLMs** compose multi-factor coverage via sequential `view` + `compute` tool calls; **human users** continue running `investorclaw analysis` / `investorclaw complete` at the CLI. Two different audiences, two different surfaces, one unchanged script layer.

### 3.6 Workflow cross-phase intents — FUTURE CONSIDERATION

Demoted from r1 per GRAEAE-r2 consensus (5 of 7 muses). Cross-phase NL queries ("what's a good allocation for my age?" crosses target + compute + implicit analyst priors) are explicitly OUT OF v2.2 SCOPE. The v2.2 tool surface supports single-intent queries per tool call; multi-intent queries are the agent's orchestration problem, not the router's. Concrete enumeration of cross-phase tool-call patterns is a separate design exercise for a future release.

This section exists as a placeholder to prevent scope creep in the v2.2 implementation.

### 3.7 News surface architecture

News splits along an **ownership axis**, not a data-shape axis:

- **Portfolio-scoped** (`portfolio_view --section=news`): news about HELD positions. Yahoo `Ticker(sym).news` per held ticker, sentiment-classified, deduped, portfolio-impact-correlated. Existing `commands/fetch_portfolio_news.py` behavior, unchanged.
- **Market-wide** (`portfolio_market --section=news --topic=X`): news about broader markets that the user does NOT necessarily hold. New in v2.2.

#### 3.7.1 Provider routing priority: FREE FIRST

All provider chains below prioritize **free, keyless endpoints** ahead of quota-gated freemium endpoints. Rationale: Yahoo costs nothing and has no quota ceiling; Finnhub / NewsAPI / Alpha Vantage / Polygon have meaningful rate limits on free tiers (60/min, 100/day, 25/day, 5/min respectively). A routing chain that hits Yahoo, SEC EDGAR, Treasury Direct, GDELT, FRED, CoinGecko, or CryptoPanic first preserves quota budget for cases where free coverage is unavailable or degraded.

For v2.2 specifically, NewsAPI is **not** part of any market-wide `portfolio_market` routing chain. Its 100/day budget is reserved by construction for `portfolio_view --section=news`, where portfolio-scoped, ticker-filtered queries make better use of the quota.

Provider classification:

| Tier | Providers | Auth | Limits |
|---|---|---|---|
| **Free / keyless** | Yahoo (yfinance + RSS + topic pages), SEC EDGAR, Treasury Direct, GDELT, LBMA daily fix | None (UA string for SEC) | Yahoo ~50 req/s soft; others effectively unlimited |
| **Free / key required** | FRED, CoinGecko (demo), CryptoPanic | Free API key | FRED 120/min; CoinGecko 30/min; CryptoPanic 500/day |
| **Freemium** | Finnhub, NewsAPI, Alpha Vantage, Polygon/Massive, Marketaux | Free tier with quotas | 60/min, 100/day, 25/day, 5/min, 100/day |

#### 3.7.2 Provider catalog — news endpoints

| Provider | Tier | Base URL | Primary news endpoint(s) | Asset coverage |
|---|---|---|---|---|
| Yahoo (yfinance) | Free/keyless | unofficial | `Ticker(sym).news` — any symbol (stocks, `^INDEX`, `=X` FX, `=F` futures, `-USD` crypto); `Search(q).news` — topic | All |
| Yahoo RSS | Free/keyless | finance.yahoo.com | `/rss/headline?s=SYM` per-ticker; `/rssindex` latest headlines | All |
| Yahoo topic pages | Free/keyless | finance.yahoo.com | `/topic/stock-market-news/`, `/topic/crypto/`, `/topic/tariffs/`, `/topic/tech/`, `/topic/latest-news/`, `/trending-tickers` | Broad |
| SEC EDGAR | Free/keyless | sec.gov/cgi-bin/browse-edgar | `?action=getcurrent&type=8-K&output=atom` (material events), `?type=13F-HR` (institutional), `?type=4` (insider) | US regulatory |
| Treasury Direct | Free/keyless | treasurydirect.gov/TA_WS | `/securities/announced?format=json`, `/securities/auctioned?format=json` | US fixed income |
| GDELT 2.0 | Free/keyless | api.gdeltproject.org/api/v2 | `/doc/doc?query=X&mode=artlist&format=json` — global news index | Global macro/events |
| FRED | Free/key | api.stlouisfed.org/fred | `/releases/updates` (data release news), `/series/observations?series_id=X` | US macro/rates |
| CoinGecko | Free/key (demo) | api.coingecko.com/api/v3 | `/news` (Plus tier), `/search/trending`, `/coins/markets` | Crypto (10K+ coins) |
| CryptoPanic | Free/key | cryptopanic.com/api/v1 | `/posts/?filter={hot\|rising\|bullish\|bearish\|important}&currencies=BTC,ETH` | Crypto |
| Finnhub | Freemium | finnhub.io/api/v1 | `/news?category={general\|forex\|crypto\|merger}`, `/company-news?symbol=X`, `/news-sentiment`, `/press-releases`, `/calendar/{economic,earnings,ipo}`, `/stock/insider-transactions` | Multi-asset |
| NewsAPI | Freemium | newsapi.org/v2 | `/top-headlines?category=business&country=us`, `/everything?q=QUERY&sortBy=publishedAt`, `/sources?category=business` | General |
| Alpha Vantage | Freemium | alphavantage.co/query | `?function=NEWS_SENTIMENT&tickers=X&topics=Y` (topics: `blockchain`, `earnings`, `ipo`, `mergers_and_acquisitions`, `financial_markets`, `economy_{fiscal,monetary,macro}`, `energy_transportation`, `finance`, `life_sciences`, `manufacturing`, `real_estate`, `retail_wholesale`, `technology`) | Multi-asset |
| Polygon / Massive | Freemium | api.polygon.io | `/v2/reference/news?ticker=X`, `/v2/reference/news?published_utc.gte=Y`, `/v2/snapshot/locale/us/markets/stocks/gainers` | Multi-asset |
| Marketaux | Freemium | api.marketaux.com/v1 | `/news/all?symbols=X&filter_entities=true` | Ticker-focused |
| LBMA | Free/keyless | lbma.org.uk/prices-and-data | Gold/silver London fix (daily CSV) | Metals spot only (no news) |

#### 3.7.3 Canonical topic vocabulary — NL triggers → topic

| NL trigger phrases | Canonical `--topic=` | Phase |
|---|---|---|
| "market news", "stock market", "what's happening", "any news", "market update" | `general` | **v2.2** |
| "forex", "currency", "FX", "dollar news", "EUR/USD", "exchange rate", "greenback" | `forex` | **v2.2** |
| "crypto", "bitcoin", "BTC", "ETH", "digital assets", "altcoins", "defi" | `crypto` | **v2.2** |
| "mergers", "M&A", "acquisitions", "takeover", "deal", "buyout" | `merger` | **v2.2** |
| "Fed", "rates", "inflation", "CPI", "economy", "policy", "tariffs", "FOMC", "Powell" | `macro` | v2.3 |
| "earnings", "who's reporting", "earnings season", "quarterly report" | `earnings` | v2.3 |
| "IPO", "going public", "new listing", "debut" | `ipo` | v2.3 |
| "tech sector", "energy sector", "financials", "sector rotation", "XLK", "industrials" | `sector` | v2.3 |
| "biggest gainers", "top movers", "trending", "most active", "biggest losers" | `movers` | v2.3 |
| "insider buying", "insider selling", "insider trades", "Form 4", "officer sold" | `insider` | v2.3 |
| "SEC filing", "8-K", "10-K", "annual report", "material event" | `filings` | v2.4+ |
| "Treasury auction", "bond auction", "T-bills", "notes", "TIPS" | `treasury` | v2.4+ |
| "oil", "WTI", "Brent", "natural gas", "grain", "corn", "wheat" | `commodities` | v2.4+ |
| "gold", "silver", "platinum", "precious metals", "GLD" | `metals` | v2.4+ |

Unknown/unimplemented topics in a given phase return a deferral envelope:

```json
{
  "status": "deferred",
  "tool": "portfolio_market",
  "section": "news",
  "topic": "<requested>",
  "reason": "Topic scheduled for v2.X",
  "available_topics": ["general", "forex", "crypto", "merger"]
}
```

#### 3.7.4 Topic × Provider routing chain (free first)

| Topic | Primary (free) | Secondary | Tertiary | Data source (non-news) |
|---|---|---|---|---|
| `general` | **Yahoo** `^GSPC`/`^DJI`/`^IXIC` `.news` + topic RSS `/topic/stock-market-news/` | Finnhub `/news?category=general` | Alpha Vantage `topics=financial_markets` | — |
| `forex` | **Yahoo** `EURUSD=X`/`DX-Y.NYB` `.news` | Finnhub `/news?category=forex` | Alpha Vantage `NEWS_SENTIMENT&topics=economy_monetary` | — |
| `crypto` | **Yahoo** `BTC-USD`/`ETH-USD` `.news` | CoinGecko `/search/trending` + CryptoPanic `/posts` | Finnhub `/news?category=crypto` | — |
| `merger` | **GDELT** `/doc/doc?query=merger+acquisition` | Finnhub `/news?category=merger` | Alpha Vantage `NEWS_SENTIMENT&topics=mergers_and_acquisitions` | — |
| `macro` | **FRED** `/releases/updates` + **GDELT** `query=federal+reserve` | Yahoo `^TNX`/`^IRX` `.news` | Alpha Vantage `topics=economy_{macro,monetary,fiscal}` | FRED series observations |
| `earnings` | **Yahoo** earnings calendar scrape | Finnhub `/calendar/earnings` | Alpha Vantage `topics=earnings` | — |
| `ipo` | **SEC EDGAR** S-1 filings RSS | Finnhub `/calendar/ipo` | Alpha Vantage `topics=ipo` | — |
| `sector` | **Yahoo** sector ETF `.news` (XLK/XLE/XLF/XLV/XLI/XLP/XLY/XLU/XLRE/XLB/XLC) | Alpha Vantage `topics=technology,finance,energy_transportation,life_sciences,manufacturing,real_estate,retail_wholesale` | Finnhub `/stock/sector-performance` | — |
| `movers` | **Yahoo** `/trending-tickers` scrape + `Search` | Polygon `/v2/snapshot/locale/us/markets/stocks/gainers` | — | — |
| `insider` | **SEC EDGAR** Form 4 RSS | Finnhub `/stock/insider-transactions` | — | — |
| `filings` | **SEC EDGAR** `?action=getcurrent&type=8-K&output=atom` | Finnhub `/press-releases` + `/company-news` filtered | — | — |
| `treasury` | **Yahoo** `^TNX`/`^FVX`/`^TYX` `.news` | **FRED** Treasury series observations | — | Treasury Direct `/securities/announced` and `/securities/auctioned` auction data |
| `commodities` | **Yahoo** `CL=F`/`NG=F`/`ZC=F`/`ZS=F` `.news` | Polygon `/v2/reference/news?ticker=CL` | Alpha Vantage `topics=energy_transportation` | — |
| `metals` | **Yahoo** `GC=F`/`SI=F`/`GLD`/`SLV` `.news` | Polygon `/v2/reference/news?ticker=GC` | Finnhub commodities news search | LBMA daily fix |

**Primary column is always free/keyless or free-tier-keyed.** Freemium providers (Finnhub, Alpha Vantage, Polygon) only appear in secondary/tertiary positions. This preserves their quota budgets for cases where the free-tier primary lacks coverage or is degraded.

NewsAPI's 100/day budget is explicitly reserved for `portfolio_view --section=news` (portfolio-scoped ticker-filtered queries), where targeted per-ticker queries yield better precision than broad market-wide headline queries. Because NewsAPI does not appear in the table above, that reservation is true by construction rather than dependent on runtime discretion.

Footnote: the `forex` Yahoo `=X` news primary and the `merger` GDELT primary are TBD empirical-verification items during v2.2 implementation. If either primary returns inadequate coverage in realistic pilot runs, the implementation promotes Finnhub to primary at runtime for that topic while keeping the documented free-first preference as the default target.

#### 3.7.5 Hierarchy

```
NEWS SURFACE (v2.2+)
│
├─ PORTFOLIO-SCOPED  [portfolio_view --section=news]
│     Uses per-ticker endpoints for HELD positions
│     Chain (free first):
│       Yahoo Ticker.news → Finnhub company-news → NewsAPI everything → Polygon
│
└─ MARKET-WIDE  [portfolio_market --section=news --topic=X]
      │
      ├─ CORE (v2.2, ships functional)  ← 4 topics matching Finnhub native categories
      │     ├─ general   [Yahoo index news → Finnhub general → Alpha Vantage]
      │     ├─ forex     [Yahoo =X → Finnhub forex → Alpha Vantage]
      │     ├─ crypto    [Yahoo -USD → CoinGecko + CryptoPanic → Finnhub crypto]
      │     └─ merger    [GDELT → Finnhub merger → Alpha Vantage]
      │
      ├─ EXTENDED (v2.3, uses existing providers)
      │     ├─ macro     [FRED + GDELT → Yahoo Treasury tickers → Alpha Vantage]
      │     ├─ earnings  [Yahoo calendar → Finnhub calendar]
      │     ├─ ipo       [SEC EDGAR S-1 → Finnhub calendar]
      │     ├─ sector    [Yahoo sector ETFs → Alpha Vantage topics]
      │     ├─ movers    [Yahoo trending → Polygon gainers]
      │     └─ insider   [SEC EDGAR Form 4 → Finnhub insider]
      │
      └─ ASSET-CLASS (v2.4+, broadens data layer)
            ├─ filings     [SEC EDGAR 8-K RSS → Finnhub press]
            ├─ treasury    [Treasury Direct auctions → FRED → Yahoo rates]
            ├─ commodities [Yahoo =F tickers → Polygon → Alpha Vantage]
            └─ metals      [Yahoo GC=F/SI=F + ETFs → Polygon → LBMA spot data]
```

#### 3.7.6 Implementation deltas for v2.2

Net-new code to ship the 4-topic market-news surface:

- `providers/price_provider.py`: add `FinnhubProvider.get_general_news(category: str) -> List[Dict]`. The `finnhub-python` SDK already exposes `general_news(category)` — just wrap it with the same error-handling pattern as `get_news()`.
- `commands/fetch_market_news.py` (~150-200 LOC): mirrors `fetch_portfolio_news.py` structure, but iterates over topic-specific sources (Yahoo index tickers / Finnhub categories / GDELT / SEC EDGAR) instead of held-position tickers. Reuses sentiment classifier, dedup logic, `rendering.compact_serializers.serialize_news_compact`.
- `runtime/router.py`: add `market --section=news --topic=X` dispatch path in `MODE_DISPATCH["market"]`.
- `SKILL.toml`: update `portfolio_market` description to advertise news capability; update `args` schema to include `topic` parameter.
- `tests/test_market_news.py` (~80 LOC): covers all 4 topics, verifies Yahoo-primary fallback chain, verifies deferral envelope for v2.3+ topics.

**No new secrets required for v2.2 core.** `FINNHUB_KEY` is already in `.env.example`; NewsAPI remains optional for `portfolio_view --section=news`. Yahoo needs no key. GDELT needs no key.

#### 3.7.7 Setup-wizard key acquisition UX

`setup/setup_wizard.py` currently prompts for Finnhub / NewsAPI / Polygon / Alpha Vantage with terse descriptions (`setup/setup_wizard.py:652-673`). v2.2 revises the wizard to **tier keys by necessity, explain what each key unlocks, and link directly to free-signup pages.** Rationale: a first-run user should understand (a) they can use InvestorClaw with zero keys via Yahoo, (b) which specific feature each optional key unlocks, (c) that every recommended key has a free tier.

Revised wizard structure (three tiers):

```
========================================
InvestorClaw runs with ZERO keys required.
Yahoo Finance covers: quotes, history, per-ticker news,
analyst consensus, index news, sector ETF news, crypto,
commodities, futures, forex.

Optional keys below UNLOCK additional features.
All recommended keys have a FREE tier.
========================================

━━━ TIER 1: RECOMMENDED (free, high value) ━━━

[1] Finnhub  —  https://finnhub.io/register  (60 req/min free)
    Unlocks: market-news categories (forex/crypto/merger),
             economic/earnings/IPO calendars,
             insider-transaction feeds.
    Skip impact: market-news falls back to Yahoo (reduced
                 merger/forex coverage); no earnings/IPO calendar.

[2] FRED  —  https://fredaccount.stlouisfed.org/apikey  (120 req/min free)
    Unlocks: authoritative macro data (Fed funds, CPI, GDP,
             Treasury yields, inflation series), data-release
             calendar for macro news topic.
    Skip impact: macro topic falls back to news-only sources;
                 no direct economic indicators.

[3] NewsAPI  —  https://newsapi.org/register  (100 req/day free)
    Unlocks: broad headline search for portfolio-specific news,
             M&A news fallback.
    Skip impact: portfolio news uses Yahoo only (still functional,
                 slightly narrower source diversity).

━━━ TIER 2: OPTIONAL (free, specialized) ━━━

[4] CryptoPanic  —  https://cryptopanic.com/developers/api/
    (500 req/day free)
    Unlocks: curated crypto news with bullish/bearish/important
             filtering.
    Skip impact: crypto topic uses Yahoo + Finnhub (still good).

[5] Alpha Vantage  —  https://www.alphavantage.co/support/#api-key
    (25 req/day free)
    Unlocks: topic-filtered news sentiment (technology, finance,
             energy_transportation, real_estate, etc.) —
             powers the v2.3 `sector` news topic.
    Skip impact: sector news uses Yahoo sector ETFs only.

━━━ TIER 3: PAID / SPECIALIZED ━━━

[6] Polygon.io  —  https://polygon.io/  (5 req/min free, paid tiers)
    Unlocks: detailed options chains, tick-level trade data,
             alternative news source for tickers without Yahoo coverage.
    Skip impact: advanced options views unavailable.

━━━ NO-KEY / AUTOMATIC ━━━

These public sources are queried automatically — no signup required:
  • Yahoo Finance       — all core price/news/fundamentals
  • SEC EDGAR           — 8-K material events, Form 4 insider filings
  • Treasury Direct     — auction announcements
  • GDELT 2.0           — global macro event news
  • LBMA daily fix      — gold/silver spot
```

Wizard behavior changes:

- **Each prompt shows direct signup URL**, not just marketing homepage (e.g., `https://finnhub.io/register`, not `https://finnhub.io`).
- **"What this unlocks" is concrete** — names the specific `--topic=` values or sections enabled. Users can match their actual needs.
- **"Skip impact" is honest** — explains what still works if the key is skipped. No FOMO tactics.
- **Tier labels** — users self-select how many keys to configure based on how deep they want coverage.
- **Automatic / no-key sources listed last** — reinforces that InvestorClaw is functional out-of-box.

Implementation delta: `setup/setup_wizard.py:_collect_provider_keys` (currently ~50 LOC) grows to ~120 LOC to accommodate the tiered structure, per-key signup URLs, unlock descriptions, and skip-impact text. Existing `_write_env_vars` is extended to include `FRED_API_KEY` and `CRYPTOPANIC_API_KEY` in the generated `.env` when provided.

Implementation also adds a small `_detect_existing_keys(env_path)` pass before each tier's prompts. It reads `~/.investorclaw/.env`; when a provider key already exists, the wizard prints `✓ [provider] already configured (edit ~/.investorclaw/.env to change)` and skips that input. Expected size: ~15 LOC.

This is the only setup-level change in v2.2. No other wizard flow changes.

## 4. Trade-offs

### Accepted

- **Per-response byte budget disciplined by staging** — see §3.0. Consolidated tools stay within 32 KB per stage, paginating when needed. No output fidelity loss vs v2.1.x; the model may need 2–3 turns to retrieve a full synthesis, which is cheap relative to the routing quality gain.
- **Richer router.py** — mode dispatch layer (~50 LOC) + stage routing (~30 LOC) = ~80 additional LOC.
- **Test-suite updates** — tests that assert specific command→script mapping need to understand mode dispatch + staging. ~25-30 test edits expected (up from 15-20 before staging added).
- **Multi-turn orchestration on the agent side** — acceptable since this is what tool-calling models are already good at. See §3.0.4.

### Rejected alternatives

- **Keep 19 tools but shorten descriptions only.** Tried in v2.1.9 already; Gemini regression remained. Description shortening helps, but tool-count overlap is the larger factor. GRAEAE consensus (Perplexity 0.88, Groq 0.80, NVIDIA 0.80) agrees the regression signals overlap, not just verbosity.
- **Split further into per-intent tools (e.g., portfolio_holdings_summary, portfolio_holdings_by_sector).** Would make the surface larger, not smaller. Codex round 1 flagged that this rejection was under-defended in r0; the defense now rests on the empirical 17→19 regression plus GRAEAE's Q1 consensus that consolidation is defensible on first principles.
- **Move everything to a single mega-tool with a `command` arg.** Too lossy for downstream models to reason about — the mode-dispatched middle ground preserves routing signal.
- **Keep `portfolio_mpt` as a standalone utility tool.** Was the r0 position. **Rejected unanimously by GRAEAE** (Perplexity, Groq, NVIDIA all voted FOLD into `compute`). MPT is computation; its distinctness from narrative recommendations doesn't justify tool-count inflation; the `mode=optimize-*` arg cleanly filters for MPT-specific queries. Opus 4.7 validation concurred.
- **Keep `identity` as a mode of `portfolio_target`.** Was the r0 position. Rejected 2-1 by GRAEAE (Groq, NVIDIA for split; Perplexity against) plus Opus 4.7 agreed with the split. Identity is persona state, not rebalancing parameters; belongs in `portfolio_config`.
- **Run a 4-arm A/B isolation test before committing.** Considered. Split vote (Gemini, NVIDIA in favor; Perplexity, Groq against). Decided: commit on first principles per GRAEAE majority on Q6 (commit) plus the practical argument that the 4-arm test takes longer than the consolidation itself. Gate the release on NL-pilot acceptance criteria (§6) instead.

## 5. Non-goals (out of v2.2 scope)

- **Any change to `commands/*.py`.** The Python scripts are correct and tested; leave them alone.
- **Any change to `runtime/router.py` beyond adding a dispatch layer.** The current COMMANDS dict, CSV-strip, tier-3 injection, auto-bootstrap, and lookup special-casing are all preserved intact.
- **Any change to the `ic_result` envelope contract.** Stages are additive metadata; absence of stage fields = single-stage envelope = today's behavior.
- **Hermes runtime fix** — needs `[[tools]]` manifest support upstream in hermes-agent. Tracked separately as an issue candidate; docs cookbook PR #15214 covers the adjacent custom_providers piece.
- **ZeroClaw runtime tool-ranking internals** — Codex couldn't inspect the Rust skill ranking code (SSH blocked mid-analysis). If ranking logic has real bugs, that's upstream work against zeroclaw-labs/zeroclaw.
- **Claude Code plugin refactor** — separate surface; works at 10/10 today.
- **OpenClaw plugin changes** — works at 10/10 today.
- **Full NL-250 benchmark run** — separate exercise; v2.2 ships with the NL-10 cross-runtime pilot as its regression gate, NL-250 follows.
- **Code-quality / maintainability refactors.** The Python layer is not under revision. Anyone filing a PR labeled "v2.2 code cleanup" is out of scope.
- **Performance tuning of the command scripts.** Unrelated to the presentation layer and unchanged.
- **i18n / non-English NL routing.** NL-250 is English-only; v2.2 does not expand that.
- **New asset classes** (futures, crypto, commodities, precious metals). The *pattern* for adding them is established in §3.1 (one tool per asset class), but v2.2 ships with only the existing `portfolio_bonds` standalone (serving both analysis and strategy sections per §3.1). New asset-class tools are v2.3+ work.

## 6. Validation plan

### 6.1 Canonical-JSON equivalence gate (MUST PASS before any NL pilot)

Before running any routing-quality test, prove that consolidation didn't change what the scripts emit. For every section-to-script mapping in `SECTION_DISPATCH`, a test asserts canonical-JSON equivalence (per §3.0.1):

```
canonical_json(output_of(investorclaw <legacy-subcommand> [args]))
    ==
canonical_json(output_of(investorclaw <consolidated-tool> --section <section> [same args]))
```

where `canonical_json()` applies: recursive dict-key sort, volatile-field strip (timestamps, `duration_ms`, PIDs, absolute paths, random seeds), whitespace normalization.

Concretely (section-dispatch mappings):

- `investorclaw holdings` ≡ `investorclaw view --section=holdings`
- `investorclaw performance` ≡ `investorclaw view --section=performance`
- `investorclaw analyst` ≡ `investorclaw view --section=analyst`
- `investorclaw news` ≡ `investorclaw view --section=news` (portfolio-scoped; per-ticker news for held positions — existing `fetch_portfolio_news.py` behavior, unchanged)
- `investorclaw market --section=news --topic=X` is **net-new** in v2.2 (no v2.1 legacy equivalent). Equivalence gate does not apply; validated by functional tests per §3.7.6 instead (`tests/test_market_news.py`)
- `investorclaw dashboard` ≡ `investorclaw view --section=dashboard`
- `investorclaw bonds` ≡ `investorclaw bonds --section=analysis` (default section; dispatches to `bond_analyzer.py`)
- `investorclaw fixed-income` ≡ `investorclaw bonds --section=strategy` (dispatches to `fixed_income_analysis.py`)
- `investorclaw synthesize` ≡ `investorclaw compute --section=synthesize`
- `investorclaw optimize sharpe` ≡ `investorclaw compute --section=optimize-sharpe`
- `investorclaw optimize minvol` ≡ `investorclaw compute --section=optimize-minvol`
- `investorclaw optimize blacklitterman` ≡ `investorclaw compute --section=optimize-blacklitterman`
- `investorclaw scenario` ≡ `investorclaw scenario --section=rebalance`
- `investorclaw stress-test` ≡ `investorclaw scenario --section=stress`
- `investorclaw rebalance-tax` ≡ `investorclaw scenario --section=tax-aware`
- `investorclaw concept` ≡ `investorclaw market --section=concept`
- `investorclaw market` ≡ `investorclaw market --section=market`
- `investorclaw session` ≡ `investorclaw target --section=allocation`
- `investorclaw update-identity` ≡ `investorclaw config --section=identity`
- `investorclaw setup` ≡ `investorclaw config --section=setup`
- `investorclaw guardrails` ≡ `investorclaw config --section=guardrails`
- `investorclaw analyze` ≡ **v2.1 legacy, points to `analyze_performance_polars.py`.** NOT part of v2.2 consolidation. Preserved as-is to avoid BC break.

### 6.1b CLI-tool-surface sync gate (per codex-r3 §3.5 concern)

To prevent the two-surface drift codex flagged (CLI permanence vs. SKILL.toml tool surface divergence over time), add a CI-enforced parity check:

- For every legacy CLI subcommand that is NOT a direct `[[tools]]` entry (notably `analysis` and `complete`), the test suite asserts there exists a documented agent-orchestration pattern that produces canonically-equivalent output. If an agent cannot reconstruct the CLI output via available tools, the CLI command has drifted beyond the tool surface and the test fails.
- Implementation: a `tests/test_cli_tool_surface_parity.py` that enumerates the set `{CLI commands} - {tool dispatch targets}` and asserts each element has an associated orchestration pattern in a new `docs/cli_orchestration_patterns.md`. The doc is the source of truth; the test enforces the sync.
- This is how v2.2 keeps the asymmetric surface (CLI broader than tools) maintainable without eventually diverging.

### 6.1c Combined `portfolio_market` gate

Add a single CI test, `tests/test_portfolio_market_combined.py`, that runs `--section=news --topic=general`, `--section=concept`, and `--section=market` against the same portfolio snapshot in the same pytest invocation. Each section passes its own gate: `news` gets a functional schema check, while `concept` and `market` get canonical-JSON equivalence against the legacy CLI. This prevents news-only tests from masking a broken deflection path.

### 6.2 Multi-section narration gate (corrected per codex-r3)

The r1 draft incorrectly named `portfolio_analyzer.py` as the multi-script orchestrator. The actual 8-stage pipeline is in `commands/portfolio_complete.py:176-231` + `internal/pipeline.py:197-332`. Updated gates:

- **Sequential coverage against the real pipeline:** issue "give me the full picture" to an agent; verify the tool-call trace covers, at minimum: `view --section=holdings`, `view --section=performance`, `portfolio_bonds` (standalone), `view --section=analyst`, `view --section=news`, `compute --section=synthesize`. Order may vary; coverage must equal what `portfolio_complete.py` produces today (modulo stages the agent chose to skip after reading earlier stage output). Order-of-calls not strict; total information coverage is.
- **CLI-parity test:** run `investorclaw complete` (legacy CLI, permanent) and the equivalent agent-orchestrated chain against the same portfolio snapshot. Both must produce canonically-equivalent output (per §3.0.1 canonical-JSON rule).
- **Staged single-section:** issue a holdings query against the 335-position test portfolio (expected to exceed 32 KB per stage); verify the agent retrieves all stages via `snapshot_id` continuation and produces a coherent summary without dropping positions. Also verify: if the portfolio CSV is modified mid-retrieval, stage N+1 is rejected with `"stale_snapshot": true` and exit_code=2.

### 6.3 Cross-runtime NL pilot (unchanged from r0)

1. Implement consolidation on a `feat/v2.2-consolidate` branch.
2. Add targeted unit tests for each consolidated tool's mode dispatch.
3. Re-run the cross-runtime NL pilot (`run_pilot_gemini_xruntime.sh`) with Gemini-flash-latest against all 3 containerized runtimes.
4. **Acceptance gates:**
   - OpenClaw: maintain 10/10 (no regression)
   - ZeroClaw master: ≥ 8/10 (up from 4–7/10)
   - Hermes: ≥ 6/10 (up from 3–5/10) — partial win acceptable; full fix is upstream
5. If gates fail, iterate description copy before cutting the release.

## 7. Rollout (revised per codex round-1 sequencing guidance)

Codex round 1 flagged that the r0 order ("consolidated tools first") churned the manifest twice. Revised order resolves contract truth FIRST, then router, then tests, then manifest:

1. `feat/v2.2-consolidate` branch on main.
2. **Contract truth commit:** reconcile SKILL.md / SKILL.toml / router.py so they agree on what `analysis`, `synthesize`, and `complete` are. (Per this RFC: `analysis` and `complete` retire as tools; `synthesize` becomes `compute:synthesize`.)
3. **Router dispatch + error semantics:** add `MODE_DISPATCH`, extend `resolve_script` with mode param, implement invalid-mode hard-fail with allowed-mode list, preserve CSV strip + tier-3 ordering.
4. **Test coverage:** update `tests/test_router.py`, `tests/test_command_contracts.py`, `tests/test_claude_plugin_contracts.py` for mode dispatch, invalid-mode behavior, script-missing behavior, CSV-strip preservation. Add targeted tests for staging contract (multi-stage retrieval, snapshot_id stability, stale-snapshot rejection).
5. **Manifest rewrite:** new `SKILL.toml` with 9 tools + tight descriptions. Legacy alias rows in `COMMANDS`.
6. **De-training pass:** rewrite `zeroclaw/SKILL.md` to use `investorclaw <subcommand>` CLI only, drop raw `pip3`/`python3` recipes (codex round 1 flagged these as training shell-bypass).
7. Tag v2.2.0-rc1 → re-run cross-runtime NL pilot with Gemini-flash-latest → check against §6 gates.
8. Tag v2.2.0 when gates pass.
9. Optional: cherry-pick routing-only subset back to v2.1.x if a maintenance release is needed.

## 8. Open questions — resolution log

**Resolved (r0 → r1):**

1. ~~`portfolio_decline` unification (concept+market+dashboard single stub vs three scripts).~~ **RESOLVED:** unified as `portfolio_market --section=concept|market`; `portfolio_market --section=news` is the default market-wide news path added in r2.2. Dashboard deferral lives under `portfolio_view --section=dashboard` per §3.1 (a different decision, reflecting the user-UX framing of dashboard as a requested view section). `concept_decline.py` + `market_decline.py` stay as underlying scripts; dispatch happens in `router.py`.
2. ~~`mode` arg: TOML `args = {mode = "..."}` schema vs positional convention.~~ **RESOLVED:** use the schema. Gemini and Claude both produce cleaner tool-call arguments against explicit parameters schemas. Codex round 2 flagged this as a ZeroClaw `SkillTool` compatibility question; verified the Rust `SkillTool.args: HashMap<String, String>` structure in `crates/zeroclaw-runtime/src/skills/mod.rs` accepts this syntax and surfaces it via `build_parameters_schema` (`tools/skill_tool.rs:44-69`).
3. ~~Alias deprecation window.~~ **RESOLVED (revised r1+):** legacy aliases are **permanent**, not deprecated. The consolidation is a presentation-layer addition to `SKILL.toml` and `SKILL.md`; the underlying CLI and script layer is not changing. Removing aliases in a later release would only hurt users (existing scripts, cron jobs, documentation, muscle memory) with zero code-quality benefit. Keep `investorclaw holdings`, `investorclaw performance`, `investorclaw optimize sharpe`, etc., working indefinitely. The stderr deprecation notice mentioned in earlier drafts is removed — nothing is being deprecated.

**Still open (for codex round 3 and/or stakeholder input):**

4. **Staging stage_key format.** Current proposal (§3.0.2) says the key should be "stable, deterministic for (tool, mode, input)". Not yet specified: is `view:holdings:accounts-1` good enough, or does it need a content-hash component for cross-run resumability? Codex round 2 flagged this gap.
5. **Cross-runtime staging support.** ZeroClaw's `SkillShellTool` at `tools/skill_tool.rs:80-150` clears env vars and uses `workspace_dir` as CWD. Does it preserve enough state for a multi-turn staged response across agent loop iterations? Claim is YES based on the ic_result file pattern but not verified end-to-end.
6. **Hermes partial improvement estimate.** §6 sets Hermes acceptance gate at ≥6/10 but the RFC doesn't explain why we expect improvement given Hermes reads SKILL.md only (not SKILL.toml). Hypothesis: the tighter SKILL.md description from the r1 work already showed Hermes moving 3/10 → 5/10. Cleaner NL triggers should continue that trend. Not a strong guarantee; gate is advisory.

---

## Appendix: migration diff sketch (r1, post-GRAEAE)

```diff
# SKILL.toml (excerpt)

 [skill]
 name = "investorclaw"
-version = "2.1.9"
+version = "2.2.0"
 ...

-[[tools]]
-name = "portfolio_holdings"
-description = "Show the user's own portfolio holdings — live prices, ... ALWAYS prefer this over memory ..."
-command = "investorclaw holdings"
-
-[[tools]]
-name = "portfolio_performance"
-description = "Analyze the user's own portfolio performance ..."
-command = "investorclaw performance"
-
-[[tools]]
-name = "portfolio_bonds"
-description = "Analyze the user's own bond holdings ..."
-command = "investorclaw bonds"
-
-[[tools]]
-name = "portfolio_analyst"
-...
-[[tools]]
-name = "portfolio_news"
-...
-[[tools]]
-name = "portfolio_dashboard"
-...

+[[tools]]
+name = "portfolio_view"
+description = "Observe the user's portfolio. Use for 'show my holdings', 'how's performance?', 'portfolio news'."
+kind = "shell"
+command = "investorclaw view --section {{section}}"
+args = { section = "holdings|performance|analyst|news|dashboard (default: holdings)" }

+[[tools]]
+name = "portfolio_compute"
+description = "Compute recommendations or MPT optima. Use for 'what do you recommend?', 'optimize Sharpe'."
+kind = "shell"
+command = "investorclaw compute --section {{section}}"
+args = { section = "synthesize|optimize-sharpe|optimize-minvol|optimize-blacklitterman (default: synthesize)" }

+[[tools]]
+name = "portfolio_target"
+description = "Set portfolio targets. Use for 'set allocation 60/30/10' or 'set drift threshold 5%'."
+kind = "shell"
+command = "investorclaw target --section {{section}}"
+args = { section = "allocation|drift (default: allocation)" }

+[[tools]]
+name = "portfolio_scenario"
+description = "Simulate scenarios. Use for 'should I rebalance?', 'stress-test 2008 crash', 'tax-aware rebalance'."
+kind = "shell"
+command = "investorclaw scenario --section {{section}}"
+args = { section = "rebalance|stress|tax-aware (default: rebalance)" }

+[[tools]]
+name = "portfolio_market"
+description = "Market-wide news + out-of-scope decline. Use for 'crypto news', 'forex news', 'M&A news', 'what is YTM?'."
+kind = "shell"
+command = "investorclaw market --section {{section}} --topic {{topic}}"
+args = { section = "news|concept|market (default: news)", topic = "general|forex|crypto|merger (only valid when section=news; default: general)" }
```

```diff
# runtime/router.py (excerpt)

 COMMANDS = {
-    "holdings": "fetch_holdings.py",
-    "performance": "analyze_performance_polars.py",
-    "bonds": "bond_analyzer.py",
+    # Consolidated v2.2 entries (dispatch via MODE_DISPATCH below)
+    "view": "__dispatch__",
+    "compute": "__dispatch__",
+    "target": "__dispatch__",
+    "scenario": "__dispatch__",
+    "market": "__dispatch__",
+
+    # Legacy aliases — permanent. Every script name here stays a valid CLI invocation indefinitely.
+    "holdings": "fetch_holdings.py",
+    "performance": "analyze_performance_polars.py",
+    "bonds": "bond_analyzer.py",
     ...
 }

+MODE_DISPATCH: dict[str, dict[str, str]] = {
+    "view": {
+        "holdings": "fetch_holdings.py",
+        "performance": "analyze_performance_polars.py",
+        "analyst": "fetch_analyst_recommendations_parallel.py",
+        "news": "fetch_portfolio_news.py",
+        "dashboard": "dashboard_decline.py",
+    },
+    "compute": {
+        "synthesize": "portfolio_analyzer.py",
+        "optimize-sharpe": "optimize.py",
+        "optimize-minvol": "optimize.py",
+        "optimize-blacklitterman": "optimize.py",
+    },
+    "target": {
+        "allocation": "session_update.py",
+        "drift": "update_identity_partial.py",
+    },
+    "scenario": {
+        "rebalance": "scenario_analysis.py",
+        "stress": "stress_test.py",
+        "tax-aware": "rebalance_tax.py",
+    },
+    "market": {
+        "news": "fetch_market_news.py",
+        "concept": "concept_decline.py",
+        "market": "market_decline.py",
+    },
+}
```

---

## 9. Roadmap (post-v2.2)

The news surface architecture (§3.7) establishes a hierarchy that extends beyond v2.2. This section codifies phased expansion.

### v2.3 — Extended news topics (existing providers)

Adds 6 more topics to `portfolio_market --section=news --topic=X`:

| Topic | Primary provider | Implementation estimate |
|---|---|---|
| `macro` | FRED `/releases/updates` + GDELT | ~80 LOC (FRED client already wired for bonds; add GDELT adapter) |
| `earnings` | Yahoo earnings calendar + Finnhub `/calendar/earnings` | ~60 LOC |
| `ipo` | SEC EDGAR S-1 RSS + Finnhub `/calendar/ipo` | ~80 LOC (add SEC EDGAR adapter) |
| `sector` | Yahoo sector ETFs (XLK/XLE/XLF/etc.) + Alpha Vantage topics | ~70 LOC |
| `movers` | Yahoo `/trending-tickers` scrape + Polygon gainers | ~90 LOC (add trending-tickers scraper) |
| `insider` | SEC EDGAR Form 4 RSS + Finnhub insider | ~60 LOC (SEC EDGAR adapter reused from `ipo`) |

**New providers wired:** SEC EDGAR (keyless), GDELT (keyless), FRED (already have key for bonds path).

**New setup-wizard entries:** FRED (if not already configured during setup), CryptoPanic (optional).

**NewsAPI quota:** stays reserved for `portfolio_view --section=news` (portfolio-scoped). v2.3 extended topics use free-tier primary + Finnhub secondary.

### v2.4+ — Asset-class expansion

Adds 4 more news topics AND 4 asset-class standalone tools:

**News topics** (under `portfolio_market --section=news --topic=X`):

| Topic | Primary provider |
|---|---|
| `filings` | SEC EDGAR `?action=getcurrent&type=8-K&output=atom` |
| `treasury` | Treasury Direct `/securities/announced` |
| `commodities` | Yahoo `=F` futures tickers |
| `metals` | Yahoo GC=F/SI=F + GLD/SLV ETFs |

**Asset-class standalone tools** (per the §3.1 "one tool per asset class" pattern, not per `section`):

| Tool | Scope | Domain model |
|---|---|---|
| `portfolio_fx` | Currency exposure — held FX positions, cross-rates | Pip-based sizing, carry-trade mechanics, forward-rate exposure |
| `portfolio_metals` | Precious + industrial metals holdings | Physical vs. paper (ETFs vs. futures vs. bullion), storage costs, spot-vs-futures basis |
| `portfolio_commodities` | Energy + ag + industrial commodity holdings | Contango/backwardation, roll yield, seasonal patterns |
| `portfolio_crypto` | Cryptocurrency holdings | Custody mode (exchange vs. self-custody), tax-lot tracking with high-freq cost basis, staking yields |

Ownership rule: `portfolio_metals` covers HELD metals positions plus metals-specific analysis; `portfolio_market --section=news --topic=metals` covers MARKET-WIDE metals news regardless of holdings. LLM routing uses the held-asset-classes list detected by auto_setup to choose between held-position analysis and broad market news. The same ownership split applies to `fx`, `commodities`, and `crypto`: standalone asset-class tools analyze what the user holds, while `portfolio_market --section=news --topic=X` covers market-wide news even when the user holds none of that asset class.

**Explicitly NOT a `portfolio_futures` tool.** Futures are an instrument type, not an asset class. A gold futures contract belongs in `portfolio_metals`; an oil futures contract belongs in `portfolio_commodities`; an S&P 500 futures contract belongs in an equities view. v2.4+ surfaces futures as overlay metadata within each asset-class tool, not as a distinct tool.

### v2.5+ — Not currently scoped

- `portfolio_options` — options chains, greeks, expiration ladders
- `portfolio_derivatives` — cross-asset derivative overlays
- `portfolio_alternatives` — private equity, hedge funds, REITs (beyond stock REITs), collectibles
- Multi-language NL routing (currently English-only)
- Cross-portfolio analytics (household-level aggregation is enterprise-tier; cross-household comparisons are not)

### Dependency graph

```
v2.2 CORE (ships now)
  ├── portfolio_market --section=news --topic=general|forex|crypto|merger
  └── setup-wizard tiered-key UX (Finnhub + FRED + NewsAPI + CryptoPanic + AlphaVantage + Polygon)
         │
         ▼
v2.3 EXTENDED (unblocked by v2.2 + SEC EDGAR adapter)
  ├── +6 topics: macro, earnings, ipo, sector, movers, insider
  ├── + SEC EDGAR adapter
  └── + GDELT adapter
         │
         ▼
v2.4+ ASSET-CLASS (unblocked by v2.3 + Treasury Direct adapter)
  ├── +4 topics: filings, treasury, commodities, metals
  ├── + Treasury Direct adapter
  └── +4 tools: portfolio_fx, portfolio_metals, portfolio_commodities, portfolio_crypto
```

No v2.3+ work is blocking v2.2. This roadmap exists for architectural continuity — the routing taxonomy, provider preference rules, and setup-wizard structure ship in v2.2 in a shape that lets each subsequent phase be purely additive.
