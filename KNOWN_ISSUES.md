# Known Issues — InvestorClaw v2.6.3

**Released:** 2026-04-30  
**Sync:** ic-engine v2.6.3, InvestorClaw v2.6.3, InvestorClaude v2.6.3

This release ships the architectural fix for InvestorClaw skill execution
in agent runtimes (zeroclaw, openclaw, hermes) — the audit-compliant skill
bundle (`build/investorclaw-skill-2.6.3.tar.gz`), build pipeline
(`make skill-bundle`), runtime installers (`installers/<runtime>/install.sh`),
and ic-engine cold-cache fix (`auto_bootstrap_holdings`).

These known issues do not block the architecture but operators should be
aware of them.

---

## ZER-1 — zeroclaw 0.7.3 default config blocks skill tool execution

**Symptom:** After installing the skill, the LLM sees `investorclaw.portfolio_ask`
and chooses to invoke it, but execution is denied with "blocked by security
policy."

**Cause:** Three default-zeroclaw autonomy gates:
1. `autonomy.forbidden_paths` includes `/home`, which contains the skill
   directory (`/home/$USER/.zeroclaw/workspace/skills/investorclaw/`).
2. `autonomy.auto_approve` does NOT include `investorclaw.*`, so the
   LLM's tool invocation requires interactive approval (which fails
   non-interactively).
3. `autonomy.allowed_commands` does NOT include `investorclaw`, blocking
   any shell-tool fallback the LLM might attempt.

**Fix:** Run `installers/zeroclaw/install.sh`. The installer auto-patches
all three gates idempotently. Manual fix: edit `~/.zeroclaw/config.toml`:
- `autonomy.forbidden_paths` — remove `/home` and `/opt`
- `autonomy.auto_approve` — append `"investorclaw.portfolio_ask"`, `"investorclaw.portfolio_refresh"`
- `autonomy.allowed_commands` — append `"investorclaw"`, `"uv"`, `"sh"`
- `skills.allow_scripts = true`

**Upstream resolution:** zeroclaw HEAD has in-flight PRs (per repo owner
2026-04-30) that may relax these gates for skill-registered tools.

---

## OC-1 — openclaw 2026.4.27 env-var-only provider auth regression

**Symptom:** `docker run -e OPENAI_API_KEY=tgp_v1_... -e OPENAI_API_BASE=https://api.together.xyz/v1 openclaw/openclaw:2026.4.27`
then `openclaw agent ...` fails with `401 Incorrect API key provided` from
`api.openai.com` — the gateway routes the Together token to OpenAI's
upstream instead of respecting `OPENAI_API_BASE`.

**Cause:** openclaw 2026.4.27 (and earlier; predates available release
history) requires explicit `~/.openclaw/agents/main/agent/auth-profiles.json`
with provider configuration. Env vars alone don't satisfy the gateway's
auth resolver.

**Workaround:** Configure `auth-profiles.json` explicitly with Together
provider mapping (TBD — codex investigation in flight to capture the
exact schema; will be in `installers/openclaw/install.sh` once known).

**Filing status:** Issue draft prepared; not yet filed at github.com/openclaw/openclaw.
Multiple adjacent regressions filed today by other reporters:
- #74886 — WhatsApp session unstable, fell back to MiniMax (similar embedded-fallback symptom)
- #74909 — `fix(pi-embedded-runner): only cooldown auth profile on real auth signals` (in-flight PR)
- #74911 — Feishu response delay 4.27 regression, "resolved by downgrading to 4.23"

This means **openclaw skill execution is currently un-validatable on Windows
without the auth-profiles workaround**. Linux containers using older
openclaw images (`ghcr.io/perlowja/openclaw-demo:latest`, private fork)
still work because they ship a pre-configured auth-profiles.json.

---

## HER-1 — hermes skill-as-tool indirection

**Symptom:** Hermes lists InvestorClaw under "Available Skills" but its
LLM tool list (28 tools: browser_*, terminal, skill_view, skill_manage,
skills_list, etc.) does NOT directly expose `investorclaw.portfolio_ask`.

**Cause:** Hermes treats skills as documentation hints injected into
system prompt rather than as directly-callable tools (different
architecture from zeroclaw 0.7.3's tool registration). The LLM has to
opt into using the skill via meta-tools (`skill_view`, `terminal`).

**Implication:** Bundle installs cleanly into hermes but invocation
reliability depends on the LLM's compliance with meta-tool indirection.
Empirically (Linux baseline 2026-04-29) hermes scored 8% (2.3/30) vs
zeroclaw's 77% (23/30) on the same prompt set.

**Path forward:** Architectural — hermes maintainers would need to
expose skill-registered tools as first-class function-calling targets.
This is the InvestorClaude (Claude Code) pattern: hardcoded slash
commands bypass LLM tool-discovery entirely.

---

## IC-1 — `investorclaw --version` reports "2.5.1" inside the bundle

**Symptom:** `investorclaw --version` prints `investorclaw 2.5.1` even
though the installed ic-engine is 2.6.3 (the cold-cache fix).

**Cause:** Cosmetic — `version.py` reads from a hardcoded constant
that wasn't bumped during the v2.6.3 sync. Does NOT affect functionality.

**Fix scope:** Trivial (single-line bump). Will land in the next
patch. ic-engine actual version is correct: `python -c 'from importlib.metadata import version; print(version("ic-engine"))'` returns `2.6.3`.

---

## Sync-release policy

Per `feedback_sync_releases_3pkg.md`: ic-engine v2.6.3, InvestorClaw v2.6.3,
InvestorClaude v2.6.3 ship together. Each tag is backed by ≥1 substantive
PR per the sync-release policy:
- ic-engine: cold-cache cascade fix in ask.py + auto_bootstrap_holdings public API + 7 regression tests + portability fixes
- InvestorClaw: audit-compliant skill bundle build pipeline + zeroclaw installer with auto-config + content sanitization for zeroclaw audit
- InvestorClaude: pin update to ic-engine v2.6.3 (delivers cold-cache fix to Claude Code users)
