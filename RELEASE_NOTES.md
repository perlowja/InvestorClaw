# InvestorClaw Release Notes

**Current: v2.5.0** (Apache 2.0, `gitlab.com/argonautsystems/InvestorClaw`)

InvestorClaw is the adapter package for Claws-family and standalone portfolio-analysis runtimes. It owns install scripts, manifests, routing contracts, and the compatibility CLI shim. The deterministic Python engine lives in [`ic-engine`](https://gitlab.com/argonautsystems/ic-engine); foundation primitives live in [`clio`](https://gitlab.com/argonautsystems/clio).

## v2.5.0

Adapter consolidation for `ic-engine` v2.5.0.

- Collapsed the agent-facing surface from 9 `portfolio_*` tools to 2 tools: `portfolio_ask` and `portfolio_refresh`.
- Pinned `ic-engine` to `v2.5.0` and aligned InvestorClaw adapter metadata to `2.5.0`.
- Updated OpenClaw, Hermes, ZeroClaw, and standalone user-facing command text to route users through `investorclaw ask "<question>"`.
- Preserved deterministic-first guardrails: finance prompts route through the signed `ic_result` path, not model memory or web search.

Migration table:

| v2.3.x tool | v2.5.0 replacement |
|-------------|--------------------|
| `portfolio_view` | `portfolio_ask` |
| `portfolio_compute` | `portfolio_ask` |
| `portfolio_target` | `portfolio_ask` |
| `portfolio_scenario` | `portfolio_ask` |
| `portfolio_market` | `portfolio_ask` |
| `portfolio_bonds` | `portfolio_ask` |
| `portfolio_config` | `portfolio_ask` |
| `portfolio_report` | `portfolio_ask` |
| `portfolio_lookup` | `portfolio_ask` |

Use `portfolio_refresh` only when the user explicitly asks to force a fresh
pipeline run or invalidate stale cached prices/news.

## v2.3.3

Pre-public-release announcement cleanup.

- Synchronized adapter version metadata across `pyproject.toml`, `investorclaw.py`, `SKILL.toml`, `openclaw.plugin.json`, and `package.json`.
- Synchronized the fallback `requirements.txt` engine pin with `pyproject.toml` and `uv.lock`: `ic-engine` `v2.4.6`.
- Cleaned public docs and manifests that still described the pre-Phase-2 monolith.
- Aligned command-surface descriptions to the current 22-command harness matrix and the 9-tool consolidated `SKILL.toml` surface.
- Removed broken references to the old top-level Claude Code implementation path. Claude Code plugin development is now in InvestorClaude; this repo keeps the forwarding marketplace entry.

## v2.3.2

Engine pin bump and CDM-vs-legacy field-name sweep.

- Bumped the adapter's `ic-engine` pin from `v2.4.2` to `v2.4.6`.
- Picked up the engine-side CDM and legacy field-name compatibility fixes for holdings, presentation, and downstream report consumers.
- Kept `clio` pinned at `v0.1.0`.

## v2.3.1

Minor post-decomposition fixes.

- Tightened adapter metadata after the Phase 2 split.
- Preserved the installed `investorclaw` shim as the adapter entry point so `.env` loading and `INVESTORCLAW_SKILL_DIR` resolution happen before delegating to `ic-engine`.
- Updated routing and marketplace scaffolding for the Claude Code plugin split.

## v2.3.0

Phase 2 of `IC_DECOMPOSITION`.

- Moved the Python portfolio engine out of this repo into `ic-engine`.
- Converted InvestorClaw into a slim adapter package: install scripts, manifests, routing contracts, harness metadata, and the compatibility CLI shim.
- Added `ic-engine` and `clio` as pinned runtime dependencies.
- Preserved the public `investorclaw` command while delegating command execution to `ic_engine.cli.main`.

## Current Surfaces

- Deterministic user entry point: `investorclaw ask "<question>"`.
- Freshness entry point: `investorclaw refresh`.
- Consolidated skill surface: [SKILL.toml](SKILL.toml) exposes `portfolio_ask` and `portfolio_refresh`.
- Install surfaces: `openclaw/install.sh`, `zeroclaw/install.sh`, `hermes/install.sh`, and the standalone `bin/setup-orchestrator` flow.
- Claude Code: forwarded through `.claude-plugin/marketplace.json` to InvestorClaude.

## Providers

Cross-runtime provider coverage is documented in [docs/AGENT-COMPARISON.md](docs/AGENT-COMPARISON.md). Local OpenAI-compatible backends include Ollama, llama-server, LMStudio, and vLLM. Market-data fallback remains `yfinance` when optional keys are not configured.

## Known Limitations

- The interactive PWA dashboard is still deferred. Dashboard requests return the canonical deferral envelope where supported.
- ZeroClaw deployments still depend on a Python environment in or around the runtime container.
- Hermes Agent provider support is constrained by the provider enum in the Hermes CLI; OpenRouter remains the practical proxy for providers that are not natively exposed.

## Validation

For this adapter repo, the release gate is:

```bash
python harness/contract_check.py
```

Engine behavior is validated in the `ic-engine` repo.

## License

Apache 2.0.
