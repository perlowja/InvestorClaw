# InvestorClaw Platform Comparison

InvestorClaw v2.1.6 runs as a skill inside five agent runtimes: Claude Code, OpenClaw, ZeroClaw, Hermes Agent, and Nemoclaw. It also runs as a standalone Python CLI for development.

This page compares Claude Code and OpenClaw. These two runtimes have the most mature InvestorClaw integration.

For ZeroClaw, Hermes Agent, and Nemoclaw, see their dedicated guides: [docs/claw/zeroclaw/README.md](claw/zeroclaw/README.md), [../hermes/README.md](../hermes/README.md), and `docs/claw/nemoclaw/`. The Nemoclaw install guide is still in progress.

## Choose a Platform Quickly

Use this table to pick the best platform for your main need.

| Your need | Best platform |
|---|---|
| Want to use Claude's AI directly? | Claude Code |
| Want to self-host on your own GPU? | OpenClaw |
| Want to integrate with existing OpenClaw agent? | OpenClaw |
| Want a simple CLI tool for portfolio analysis? | Claude Code |
| Want custom LLM provider (Together.ai, Groq, etc.)? | OpenClaw |

## Features

Claude Code and OpenClaw share most core portfolio features. Claude Code adds stronger interactive features. OpenClaw adds more provider flexibility and professional controls.

| Feature | Claude Code | OpenClaw | Notes |
|---|---|---|---|
| Holdings analysis | ✅ | ✅ | Identical functionality |
| Performance metrics | ✅ | ✅ | Same calculations |
| Bond analytics | ✅ | ✅ | YTM, duration, credit quality |
| Analyst consensus | ✅ | ✅ | Wall Street ratings |
| News sentiment | ✅ | ✅ | Portfolio-correlated headlines |
| Portfolio optimization | ✅ | ✅ | Rebalancing suggestions |
| Multi-factor synthesis | ✅ | ✅ | LLM-powered insights |
| EOD HTML report | ✅ | ✅ | Email-ready summary |
| CSV/Excel export | ✅ | ✅ | Holdings + metrics |
| Stonkmode narration | ✅ | ✅ | Comedy mode with personas |
| Interactive dashboard | ⏳ deferred | ⏳ deferred | PWA dashboard is in development. Ask dashboard questions through `/portfolio ask`; it returns the current deferral envelope where applicable. |
| Vision extraction | ✅ | ❌ | Broker statement OCR (Claude vision) |
| Multi-file auto-consolidation | ✅ | ❌ | Multiple broker CSVs in one turn |
| Conversation history | ✅ | ❌ | Follow-up Q&A within same context |
| Local LLM inference (optional) | ✅ | ✅ | Ollama, llama-server (for offline analysis) |
| Custom narrative providers | ❌ | ✅ | Together.ai, Groq, OpenAI, NGC (OpenClaw flexibility) |
| HMAC audit trails (optional) | ✅ | ✅ | Synthesis integrity verification |
| Professional guardrails | ❌ | ✅ | FA Professional mode (relaxed guardrails) |

ZeroClaw also supports Together, Groq, and OpenAI through its OpenAI-compatible provider plugin.

Hermes Agent supports the same endpoints through the OpenRouter proxy. A native Together/Groq/OpenAI/Perplexity provider set for Hermes Agent is tracked as a planned upstream PR.

## Install and Set Up

Claude Code needs less setup. OpenClaw gives you more control.

### Claude Code

```text
/plugin marketplace add https://gitlab.com/argonautsystems/InvestorClaude.git
/plugin install investorclaw@investorclaude
```

After official Anthropic marketplace acceptance, run:

```text
/plugin install investorclaw@claude-plugins-official
```

Claude Code does not require a manual clone or Python dependency installation. The plugin loads directly, and the bundled setup skill prepares the runtime.

### OpenClaw

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
```

For standalone development, use `git clone` and then run `bash ./claude/bin/setup-orchestrator`.

## Data Flow

Claude Code sends summarized portfolio data to Claude. OpenClaw lets you choose whether to send data at all.

### Claude Code

```text
Your Portfolio (CSV/XLS/PDF)
    ↓
Python Computation (on your machine)
    ↓
Claude Code Context (Haiku/Sonnet)
    ↓
Results + interactive artifacts
```

Only summarized portfolio data goes to Claude. That data includes tickers, values, and returns. No account numbers or PII go to Claude.

### OpenClaw

```text
Your Portfolio (CSV/XLS/PDF)
    ↓
Python Computation (on your machine)
    ↓
Configurable Narrative Provider (default: local Ollama)
    ├─ Local: Ollama / llama-server (no transmission)
    ├─ Cloud: Together.ai, Groq, OpenAI, custom (opt-in)
    └─ Disabled: Just Python output
    ↓
Results to stdout
```

OpenClaw makes data transmission configurable. The default is local Ollama. Cloud providers receive summarized portfolio text only.

## Commands

Claude Code uses the `/ic-*` namespace. OpenClaw uses the `/portfolio *` namespace.

### Claude Code

```bash
/ic-holdings          # Holdings snapshot
/ic-performance       # Performance metrics
/ic-bonds             # Bond analytics
/ic-analysis          # Full narrative pipeline (replaces the deferred dashboard)
/ic-optimize          # Rebalancing suggestions
/ic-help              # All commands
```

Namespace: `/ic-*` (InvestorClaw commands)

### OpenClaw

```bash
/portfolio ask "What's in my portfolio?"
/portfolio ask "How am I doing?"
/portfolio ask "Show my bond exposure"
/portfolio refresh
```

Namespace: `/portfolio *` (generic portfolio commands)

For standalone development, run:

```bash
investorclaw ask "What's in my portfolio?"
```

## Configuration

Claude Code works without configuration. OpenClaw uses a configuration file.

### Claude Code

No configuration is required. Claude Code uses Anthropic models such as Haiku and Sonnet by default.

For optional local inference, run:

```bash
/ic-llm-config
```

This command guides setup for local Ollama or llama-server for offline analysis.

### OpenClaw

Configuration file: `~/.investorclaw/.env`

Key settings:

```bash
# Narrative provider (default: ollama)
INVESTORCLAW_NARRATIVE_PROVIDER=ollama
INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:11434

# Optional: Cloud provider
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=your-key
```

To open the setup wizard, run:

```bash
/portfolio llm-config
```

This interactive wizard lets you choose a provider. Options include Ollama, Together.ai, NGC, custom, or disabled.

## Cost

Claude Code has predictable low usage costs. OpenClaw costs depend on your provider and hardware.

### Claude Code

- Haiku-only: ~$0.05/month (basic holdings + performance)
- Haiku + Sonnet: $0.25-$2.00/month (synthesis + full analysis pipeline)

Anthropic handles pricing through standard API rates. Claude Code is Anthropic's first-party runtime, so no agent-tier surcharge applies. A free tier is available for new users.

### OpenClaw

- Local (Ollama/llama-server): $0 (requires GPU, 24GB+ VRAM)
- Cloud (Together.ai, Groq, OpenAI, xAI, Google, NVIDIA NIM, Perplexity): varies by provider
- Together.ai: free tier (100 calls/month) + paid options
- Groq: free tier (30 req/min, 14.4K req/day)
- OpenAI: $0.50-$2.00/month depending on model
- xAI / Google Gemini / NVIDIA NIM: pay-as-you-go
- Custom: depends on your infrastructure

> [!WARNING]
> Anthropic via OpenClaw / ZeroClaw / Hermes Agent is not the same as Claude Code.
>
> Effective April 4, 2026, Anthropic subscriptions (Pro $20/mo, Max $100-$200/mo) no longer cover use from third-party agent runtimes. No subscription tier authenticates those calls.
>
> To use Claude from OpenClaw / ZeroClaw / Hermes Agent, enable Anthropic's pay-as-you-go "extra usage" billing or connect with a direct API key on metered billing.
>
> Claude Code is unaffected because it is first-party. It still works with subscription at standard rates.
>
> If you want Claude, use Claude Code directly. If you already run a third-party agent, the fleet default stack is MiniMax-via-Together for narrative + Gemma4 for consultation.
>
> Source: [PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2026/third-party-agents-lose-access-as-anthropic-tightens-claude-usage-rules/) · [VentureBeat](https://venturebeat.com/technology/anthropic-cuts-off-the-ability-to-use-claude-subscriptions-with-openclaw-and)
>
> Boris Cherny (head of Claude Code): "subscriptions were never designed for the kind of continuous, automated demand these tools generate."

## When to Choose Claude Code

Choose Claude Code if you want the simplest setup and the strongest built-in interactive experience.

- You want zero configuration and an out-of-box setup.
- You prefer conversational Q&A such as "Why is tech concentrated?"
- You want interactive charts and dashboards with inline Plotly artifacts.
- You want vision extraction for broker statements.
- You want multi-turn context in one thread.
- You are comfortable with a cloud-based LLM through Anthropic at about ~$0.05-$2.00/month.

## When to Choose OpenClaw

Choose OpenClaw if you want more control over providers, infrastructure, and compliance posture.

- You want full control over the narrative provider, including Together.ai, Groq, OpenAI, and custom options.
- You prefer local inference with Ollama or llama-server and no cloud transmission.
- You have a GPU and want zero recurring costs beyond hardware.
- You are integrating with an existing OpenClaw agent.
- You need audit trails for professional or compliance deployments.
- You work in regulated industries that require on-premises processing.
- You want optional guardrail relaxation for financial advisor workflows.

## Support and Resources

Use the runtime-specific docs first. Then use the shared docs for security, features, and commands.

### Claude Code

- Docs: `/claude/README.md` (this directory)
- Setup: `/claude/INSTALL_FLOW.md`
- Commands: `claude-code /ic-help`

### OpenClaw

- Docs: `README.md` (root)
- Quick Start: `QUICKSTART.md`
- Setup: `CONFIGURATION.md`
- Commands: `/portfolio ask "<question>"`, `/portfolio refresh`

### Shared Resources

- Security (vulnerability reporting): `SECURITY.md`
- Security model (data flow): `docs/DATA_FLOW.md`, `SECURITY.md`
- Features: `FEATURES.md` (OpenClaw) or `/claude/README.md` (Claude Code)
- All commands: `docs/COMMAND_INDEX.md`

## More Information

For data privacy details, see `docs/DATA_FLOW.md`.

For release-notes-style history, see `RELEASE_NOTES_v1.2.0.md`.
