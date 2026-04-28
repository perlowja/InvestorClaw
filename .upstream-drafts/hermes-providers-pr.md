# Add native providers: Together, Groq, OpenAI (direct), Perplexity

## Summary

Adds four first-class provider entries to Hermes Agent's `PROVIDER_REGISTRY` + `hermes chat --provider` argparse choices. All four are OpenAI-compatible endpoints that the agent already talks to happily via OpenRouter today — but that extra hop adds latency, a credit wrapper, and a confusing debugging surface when the underlying provider changes. Direct native adapters match the pattern used for `gemini`, `xai`, `nvidia`, `zai`, `kimi-coding`, `stepfun`, and `ollama-cloud`.

## Motivation

Downstream skill integrations (e.g., InvestorClaw) publish a provider matrix that promises support for Together, Groq, OpenAI, and Perplexity via CLI runtimes. OpenClaw and ZeroClaw deliver on this natively; Hermes Agent currently requires either:

1. An OpenRouter account and `--provider openrouter` (extra cost wrapper, breaks direct-billing expectations), or
2. `custom_providers:` in `config.yaml` — which the schema accepts but `hermes chat --provider` argparse rejects because the enum is hardcoded (`main.py` line ~1440).

Result: users pick OpenRouter-proxy and then have to explain why their Together credits aren't being consumed, or they edit `config.yaml` and get a confusing argparse error. Four native provider entries make the user-facing behavior consistent with the runtime's own schema.

## Provider specs (canonical, verified against each vendor's API 2026-04-24)

| Provider | `id` | Inference base URL | Auth | Env-var precedence | Verified |
|---|---|---|---|---|---|
| Together AI | `together` | `https://api.together.xyz/v1` | `Authorization: Bearer <key>` | `TOGETHER_API_KEY` | `GET /v1/models` → 200, 240 models listed |
| Groq | `groq` | `https://api.groq.com/openai/v1` | `Authorization: Bearer <key>` | `GROQ_API_KEY` | `GET /openai/v1/models` → 200 |
| OpenAI (direct) | `openai` | `https://api.openai.com/v1` | `Authorization: Bearer <key>` | `OPENAI_API_KEY` | `GET /v1/models` → 200, 122 models |
| Perplexity | `perplexity` | `https://api.perplexity.ai` | `Authorization: Bearer <key>` | `PPLX_API_KEY`, `PERPLEXITY_API_KEY` | `POST /chat/completions` → 200 (no `/models` endpoint) |

All four are OpenAI-compatible chat-completions wire format. Perplexity adds a `citations` field on responses and exposes a `sonar` family plus several `sonar-*` reasoning variants; the base URL is `https://api.perplexity.ai` (note: NO `/v1` prefix — unlike the other three). This is a canonical quirk of the Perplexity API, not a bug.

## Code changes

### 1. `hermes_cli/auth.py` — four new `ProviderConfig` entries in `PROVIDER_REGISTRY`

Add after the existing `"gemini"` entry (alphabetical-ish), following the pattern established by gemini/zai/kimi-coding:

```python
    "together": ProviderConfig(
        id="together",
        name="Together AI",
        auth_type="api_key",
        inference_base_url="https://api.together.xyz/v1",
        api_key_env_vars=("TOGETHER_API_KEY",),
        base_url_env_var="TOGETHER_BASE_URL",
    ),
    "groq": ProviderConfig(
        id="groq",
        name="Groq",
        auth_type="api_key",
        inference_base_url="https://api.groq.com/openai/v1",
        api_key_env_vars=("GROQ_API_KEY",),
        base_url_env_var="GROQ_BASE_URL",
    ),
    "openai": ProviderConfig(
        id="openai",
        name="OpenAI",
        auth_type="api_key",
        # The OpenAI direct API. Distinct from `openai-codex` (ChatGPT
        # subscriber OAuth flow, different endpoint + auth shape).
        inference_base_url="https://api.openai.com/v1",
        api_key_env_vars=("OPENAI_API_KEY",),
        base_url_env_var="OPENAI_BASE_URL",
    ),
    "perplexity": ProviderConfig(
        id="perplexity",
        name="Perplexity",
        auth_type="api_key",
        # NOTE: Perplexity's base URL has NO /v1 path — chat completions
        # live at /chat/completions off the root domain. This is
        # vendor-canonical; do not append /v1.
        inference_base_url="https://api.perplexity.ai",
        api_key_env_vars=("PPLX_API_KEY", "PERPLEXITY_API_KEY"),
        base_url_env_var="PPLX_BASE_URL",
    ),
```

### 2. `hermes_cli/main.py` — argparse `--provider` choices

Extend the list at `main.py:~1440` from current:

```python
choices=[
    "auto",
    "openrouter",
    "nous",
    "openai-codex",
    "copilot-acp",
    "copilot",
    "anthropic",
    "gemini",
    "xai",
    "ollama-cloud",
    "huggingface",
    "zai",
    "kimi-coding",
    "kimi-coding-cn",
    "stepfun",
    "minimax",
    "minimax-cn",
    "kilocode",
    "xiaomi",
    "arcee",
    "nvidia",
],
```

to:

```python
choices=[
    "auto",
    "openrouter",
    "nous",
    "openai-codex",
    "copilot-acp",
    "copilot",
    "anthropic",
    "gemini",
    "xai",
    "ollama-cloud",
    "huggingface",
    "zai",
    "kimi-coding",
    "kimi-coding-cn",
    "stepfun",
    "minimax",
    "minimax-cn",
    "kilocode",
    "xiaomi",
    "arcee",
    "nvidia",
    # OpenAI-compatible API providers (new in this PR)
    "together",
    "groq",
    "openai",
    "perplexity",
],
```

### 3. `agent/model_metadata.py` — `_PROVIDER_PREFIXES` + URL inference

Extend the frozenset so `together/<model>` / `groq/<model>` / `openai/<model>` / `perplexity/<model>` prefixes are recognized for model-catalog lookups:

```python
_PROVIDER_PREFIXES: frozenset[str] = frozenset({
    # ... existing entries ...
    "together", "together-ai",      # Together AI
    "groq",                         # Groq
    "openai", "gpt",                # OpenAI direct (distinct from openai-codex)
    "perplexity", "pplx", "sonar",  # Perplexity
})
```

And in the base-URL → provider inference table (`_infer_provider_from_url` lookup dict nearby):

```python
    "api.together.xyz": "together",
    "api.groq.com": "groq",
    "api.openai.com": "openai",
    "api.perplexity.ai": "perplexity",
```

### 4. `hermes_cli/auth_commands.py` — if the `hermes auth add` positional `provider` has its own enum validator, add the four strings there too

(Check: `hermes auth add --help` currently shows *"provider: Provider id (for example: anthropic, openai-codex, openrouter)"* — the help string is examples-only; the validator may already defer to `PROVIDER_REGISTRY`. Verify during the PR and include an `auth_commands.py` hunk only if needed.)

## Test plan

```bash
# Per-provider smoke (set the matching *_API_KEY env first)
for p in together groq openai perplexity; do
    hermes chat -q "Reply OK." --provider "$p" --yolo
done
```

Each invocation should return "OK" with `Messages: 2 (1 user, 0 tool calls)` in the hermes session footer — matching the current `xai` / `gemini` / `nvidia` baselines. No OpenRouter credits consumed.

Model-choice smoke (using each provider's default flagship):

```bash
hermes chat --provider together  -m MiniMaxAI/MiniMax-M2.7            -q "Reply OK." --yolo
hermes chat --provider groq      -m llama-3.3-70b-versatile           -q "Reply OK." --yolo
hermes chat --provider openai    -m gpt-5.4                           -q "Reply OK." --yolo
hermes chat --provider perplexity -m sonar                             -q "Reply OK." --yolo
```

## Scope intentionally excluded

- **`custom_providers:` CLI un-block.** Separate concern — worth a follow-up PR but out of scope here. The argparse enum and the schema-level custom_providers path should converge; that's its own design call.
- **OAuth flows.** All four providers offered here are API-key auth. Together/Groq/Perplexity don't offer OAuth device-code; OpenAI direct's OAuth path is covered by `openai-codex`.
- **Model catalogs.** The four providers already live in models.dev and are resolved via `_infer_provider_from_url` once the prefix entries (§3 above) are in place. No hardcoded catalog additions required.
- **Anthropic as a recommended option.** Hermes Agent already has a native `anthropic` provider and this PR does not change it. Worth flagging in release notes though: **effective April 4, 2026, Anthropic subscriptions (Pro $20/mo, Max $100–$200/mo) no longer cover use from third-party agent runtimes at all** — the subscription will not authenticate Hermes Agent's calls to Claude. Users picking `--provider anthropic` need pay-as-you-go "extra usage" billing on the subscription *or* a direct API key with metered billing. A user-facing heads-up in `hermes model` (interactive wizard) when `anthropic` is selected — pointing to that policy change — would be a good follow-up issue. Source: [PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2026/third-party-agents-lose-access-as-anthropic-tightens-claude-usage-rules/).

## InvestorClaw context (for reviewer context — not requesting action here)

InvestorClaw is an open-source FINOS CDM 5.x portfolio-analysis skill ([github.com/perlowja/InvestorClaw](https://github.com/perlowja/InvestorClaw)) that runs inside five agent runtimes including Hermes Agent. Its v2.1.6 provider-support matrix explicitly documents the native-vs-proxy gap this PR closes. Adopting these four providers lets Hermes Agent stay parity with OpenClaw/ZeroClaw on the skill's published integration surface.

## Attribution

Filed in personal capacity.
