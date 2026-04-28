# InvestorClaw

<p align="center">
  <picture>
    <source srcset="https://cdn.jsdelivr.net/gh/argonautsystems/InvestorClaw@main/assets/investorclaw-logo.webp" type="image/webp">
    <img src="https://cdn.jsdelivr.net/gh/argonautsystems/InvestorClaw@main/assets/investorclaw-logo.jpg" alt="InvestorClaw Logo" width="200" loading="lazy"/>
  </picture>
</p>

Portfolio analysis and market intelligence | v2.6.0 | Apache 2.0 License

> ⚠️ The dashboard is in development and is not shipped in the default install. Ask dashboard questions through `investorclaw ask "<question>"`; the deterministic engine returns the current deferral envelope where applicable.

InvestorClaw is the adapter package for Claws-family and standalone portfolio analysis. It ships install scripts, manifests, routing contracts, and the back-compatible CLI shim.

The deterministic portfolio engine lives in [`ic-engine`](https://gitlab.com/argonautsystems/ic-engine). Foundation primitives live in [`clio`](https://gitlab.com/argonautsystems/clio).

Optional [Stonkmode](docs/STONKMODE.md) adds live commentary from 30 fictional cable TV finance personalities.

---

## Features

InvestorClaw separates runtime adapters from engine computation.

- Adapter package. This repo owns Claws-family manifests, setup scripts, routing contracts, and the `investorclaw` shim. Portfolio math and CDM 5.x modeling are implemented in `ic-engine`; LLM narrative synthesis sits on top of structured engine output.
- v2.5 deterministic surface. `ic-engine` provides holdings, performance, bond analytics, optimization, scenario/rebalancing, lookup, reporting, and deflection envelopes. This adapter exposes them through `investorclaw ask "<question>"`, which eagerly runs the deterministic pipeline, stores an HMAC-signed JSON envelope, and narrates from authoritative output.
- Six asset classes. The CDM 5.x portfolio model supports equity, bond, crypto, futures, metals, and cash.
- Current command coverage. The adapter surface is two commands: `investorclaw ask` for natural-language portfolio questions and `investorclaw refresh` for explicit fresh pipeline runs. Historical backend command coverage remains in [harness/command_matrix.py](harness/command_matrix.py) for compatibility checks.
- Pluggable providers. Cloud providers include Together AI, Google, xAI, OpenAI, Groq, Anthropic, Perplexity, and NVIDIA NIM. Local providers include Ollama, llama-server, LMStudio, and vLLM.
- Safe fallback defaults. InvestorClaw uses `yfinance` by default when no keys are configured. `yfinance` is free and unlimited.

Native cross-runtime coverage varies.

See [docs/AGENT-COMPARISON.md](docs/AGENT-COMPARISON.md) § Model backend for the per-runtime provider matrix.

> Note: Effective April 4, 2026, Anthropic Claude subscriptions (Pro at $20/mo and Max at $100–$200/mo) no longer cover use from third-party agent runtimes like OpenClaw, ZeroClaw, or Hermes Agent. The plan limits do not apply there, and a subscription alone will not authenticate those calls.
>
> To use Claude models from a third-party agent, either enable pay-as-you-go "extra usage" billing on the subscription or connect with a direct API key on metered billing.
>
> Claude Code is different. Anthropic subscriptions continue to apply normally there at standard rates.
>
> The fleet default stack for non-Claude-Code runtimes is therefore MiniMax-via-Together for narrative and Gemma4 for consultation. Use Claude Code if you want Claude.
>
> Sources: [PYMNTS 2026-04-04](https://www.pymnts.com/artificial-intelligence-2/2026/third-party-agents-lose-access-as-anthropic-tightens-claude-usage-rules/), [VentureBeat](https://venturebeat.com/technology/anthropic-cuts-off-the-ability-to-use-claude-subscriptions-with-openclaw-and)

---

## Non-Goals

InvestorClaw helps you have informed conversations with your financial advisor by surfacing data-driven insights.

It does not manage money.

It does not execute trades.

It does not provide investment advice.

---

## Comparison With thinkorswim

InvestorClaw helps you understand your portfolio. thinkorswim helps you execute trades.

|  | InvestorClaw | thinkorswim |
|---|---|---|
| Purpose | Portfolio analysis & insights | Active trading & execution |
| Can trade? | ❌ No | ✅ Yes |
| Data source | Free (yfinance, Polygon, Finnhub) | Real-time (proprietary) |
| Run locally? | ✅ Yes (with Ollama) | ❌ Cloud only |
| Open source? | ✅ Yes (Apache 2.0) | ❌ Proprietary |
| Target user | Individual investors + advisors | Professional/active traders |
| Best for | Understanding your portfolio | Executing trades + charting |

Use InvestorClaw to analyze.

Use thinkorswim to execute.

Use both if you want analysis and execution in one workflow.

---

## Quick Start

InvestorClaw supports Claws-family and standalone deployment paths from this adapter repo.

Choose the platform that matches how you work.

### Claude Code

The Claude Code plugin lives in a separate repo at [gitlab.com/argonautsystems/InvestorClaude](https://gitlab.com/argonautsystems/InvestorClaude). InvestorClaw does not ship a Claude Code marketplace; install directly from InvestorClaude using Anthropic's marketplace flow:

```text
/plugin marketplace add https://gitlab.com/argonautsystems/InvestorClaude.git
/plugin install investorclaw@investorclaude
```

After official Anthropic marketplace acceptance, the install will route through `/plugin install investorclaw@claude-plugins-official`.

See the [InvestorClaude README](https://gitlab.com/argonautsystems/InvestorClaude/-/blob/main/README.md) for the deterministic ask/refresh interaction model, slash-command reference, and bootstrap flow. Do not clone the InvestorClaw repo for Claude Code use — Claude Code installs from InvestorClaude directly.

---

### OpenClaw

OpenClaw fits Linux and macOS workstations and servers.

Install InvestorClaw as an OpenClaw skill:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
```

Then use:

```text
/portfolio ask "What's in my portfolio?"
/portfolio ask "How am I doing?"
/portfolio refresh
```

See [docs/claw/openclaw/README.md](docs/claw/openclaw/README.md).

---

### ZeroClaw

ZeroClaw fits Raspberry Pi and other ARM devices.

Install InvestorClaw on ARM devices such as Raspberry Pi 4 and 5:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/zeroclaw/install.sh | bash
```

Then use:

```text
/portfolio ask "Show my bond exposure"
/portfolio refresh
```

See [docs/claw/zeroclaw/zeroclaw_install.md](docs/claw/zeroclaw/zeroclaw_install.md).

---

### Hermes Agent

Hermes Agent installs InvestorClaw inside the NousResearch agentic CLI.

Install InvestorClaw as a skill inside the **Hermes Agent** runtime ([github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)).

Hermes Agent is the agentic CLI.

It is not a model.

You can pair it with any provider the agent supports. That includes cloud providers such as OpenAI, Together, xAI, OpenRouter, and Nous Portal. It also includes fully local providers such as Ollama, vLLM, llama-server, and LMStudio.

> Note: The Hermes LLM family (Hermes 3, Hermes 4 — NousResearch fine-tunes of Llama/Qwen) is a separate product. Hermes Agent can use a Hermes LLM as its backend model, or any other model.

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash
```

Then use:

```text
investorclaw ask "What's in my portfolio?"
investorclaw ask "How am I doing?"
investorclaw refresh
```

See [hermes/README.md](hermes/README.md).

---

### Standalone Python CLI

Use the standalone Python CLI for development or local use without agent runtimes.

Step 1: Run the automated setup orchestrator.

```bash
# Clone the repository (one-time)
git clone https://gitlab.com/argonautsystems/InvestorClaw.git
cd InvestorClaw

# Run the setup orchestrator (handles uv, venv, dependencies, wizard)
bash ./bin/setup-orchestrator
```

The script automatically:

- Detects or installs `uv` if needed.
- Creates an isolated Python virtual environment.
- Installs all dependencies.
- Runs the portfolio setup wizard.
- Works on macOS, Linux, and Windows (WSL).

Step 2: Use InvestorClaw.

After setup completes, activate the environment and run commands:

```bash
source ./.venv/bin/activate  # or .\.venv\Scripts\activate on Windows

# Commands
investorclaw ask "What's in my portfolio?"
investorclaw ask "Generate an end-of-day report"
investorclaw refresh
```

See [bin/README.md](bin/README.md) for orchestrator details.

No API keys are required.

InvestorClaw falls back to `yfinance`, which is free and unlimited.

Optional keys unlock analyst ratings, news, and premium data.

See [docs/claude/CLAUDE_QUICKSTART.md](docs/claude/CLAUDE_QUICKSTART.md) for Claude Code setup details.

See [ARCHITECTURE_INDEX.md](docs/ARCHITECTURE_INDEX.md) for architecture details.

---

## EOD Report

Ask InvestorClaw to generate an HTML email report that summarizes your portfolio at end of day.

```text
investorclaw ask "Generate my end-of-day portfolio report"
investorclaw ask "Generate my end-of-day report and email it to you@example.com"
```

<p align="center">
  <picture>
    <source srcset="https://cdn.jsdelivr.net/gh/argonautsystems/InvestorClaw@main/assets/eod-report-sample.webp" type="image/webp">
    <img src="https://cdn.jsdelivr.net/gh/argonautsystems/InvestorClaw@main/assets/eod-report-sample.jpg" alt="InvestorClaw EOD report — end-of-day portfolio analysis" width="700" loading="lazy"/>
  </picture>
</p>

The report includes:

- Real-time prices
- Performance metrics
- Sector breakdown
- News sentiment
- Email-ready HTML with a dark theme
- Mobile-responsive layout

---

## Documentation

InvestorClaw runs as a Claws-family skill and as a standalone Python CLI. Claude Code support is maintained in the split InvestorClaude plugin.

Use the Quick Start section to choose a path.

### Supported Agent Runtimes

| Runtime | Vendor | What it is | Quick start |
|---|---|---|---|
| Claude Code | Anthropic | Separate InvestorClaude plugin; this repo forwards marketplace installs | [docs/claude/README.md](docs/claude/README.md) |
| OpenClaw | Open-source | Agentic CLI + gateway (WebSocket, web UI, plugin SDK) | [docs/QUICKSTART_OPENCLAW.md](docs/QUICKSTART_OPENCLAW.md) → [docs/claw/openclaw/README.md](docs/claw/openclaw/README.md) |
| ZeroClaw | Open-source (Rust) | Lightweight agent runtime. It is edge-native and Raspberry Pi / ARM friendly. | [docs/claw/zeroclaw/zeroclaw_install.md](docs/claw/zeroclaw/zeroclaw_install.md) → [docs/claw/zeroclaw/README.md](docs/claw/zeroclaw/README.md) |
| Hermes Agent | NousResearch | Agentic CLI ([github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)). Not to be confused with the Hermes LLM family, which is a separate NousResearch model product. Hermes Agent can use a Hermes LLM as its backend, or any other provider it supports. | [hermes/README.md](hermes/README.md) |
| Nemoclaw | NousResearch (edge) | Nclawzero-derived edge agent runtime for low-power hardware. It ships as a Yocto-based distro (`nclawzero`) for Raspberry Pi and Jetson. | *(install guide in progress)* |

Standalone Python CLI: development or offline use without an agent runtime. See [QUICKSTART.md](QUICKSTART.md) Option 5 and [bin/README.md](bin/README.md).

### Claude Code and Claude API

| Page | What's there |
|------|--------------|
| [docs/claude/README.md](docs/claude/README.md) | Overview of Claude platforms |
| [docs/claude/CLAUDE_API_INTEGRATION_OPPORTUNITIES.md](docs/claude/CLAUDE_API_INTEGRATION_OPPORTUNITIES.md) | Claude API integration guide |
| [docs/claude/CLAUDE_TESTING_AUTOMATION.md](docs/claude/CLAUDE_TESTING_AUTOMATION.md) | Testing strategy for plugin development |

### OpenClaw, ZeroClaw, and Hermes Agent

| Page | What's there |
|------|--------------|
| [docs/claw/README.md](docs/claw/README.md) | Overview of OpenClaw and ZeroClaw (shared architecture) |
| [docs/claw/openclaw/README.md](docs/claw/openclaw/README.md) | OpenClaw skill integration |
| [docs/claw/zeroclaw/zeroclaw_install.md](docs/claw/zeroclaw/zeroclaw_install.md) | ZeroClaw config & troubleshooting (Raspberry Pi / ARM) |
| [docs/claw/zeroclaw/README.md](docs/claw/zeroclaw/README.md) | ZeroClaw overview |
| [hermes/README.md](hermes/README.md) | Hermes Agent skill setup (any provider, cloud or local) |

### Shared Claw Architecture

| Page | What's there |
|------|--------------|
| [docs/claw/shared/README.md](docs/claw/shared/README.md) | Common patterns across Claw platforms |
| [docs/claw/shared/PLATFORM_COMPARISON.md](docs/claw/shared/PLATFORM_COMPARISON.md) | OpenClaw vs. ZeroClaw vs. Claude Code side-by-side |
| [docs/claw/shared/LOCAL_INFERENCE_GUIDE.md](docs/claw/shared/LOCAL_INFERENCE_GUIDE.md) | Setup Ollama/vLLM/llama-server for offline analysis |

### Commands and Features

| Page | What's there |
|------|--------------|
| [docs/COMMAND_INDEX.md](docs/COMMAND_INDEX.md) | Historical backend command reference |
| [docs/STONKMODE.md](docs/STONKMODE.md) | Entertainment mode + Dr. Stonk financial education |

### Current Command Surfaces

| Surface | Source of truth | Scope |
|---------|-----------------|-------|
| CLI commands | [SKILL.toml](SKILL.toml) | `investorclaw ask` and `investorclaw refresh` |
| Skill tools | [SKILL.toml](SKILL.toml) | `portfolio_ask` and `portfolio_refresh` |
| Historical backend matrix | [harness/command_matrix.py](harness/command_matrix.py) | Backend compatibility commands retained for harness checks |

### Architecture and Design

| Page | Audience | What's there |
|------|----------|--------------|
| [ARCHITECTURE_INDEX.md](docs/ARCHITECTURE_INDEX.md) | Everyone | Navigation guide for architecture docs |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Contributors | Code module organization and structure |
| [ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md) | Tech Leads | Design principles and production rationale |
| [ARCHITECTURE_MODELS.md](docs/ARCHITECTURE_MODELS.md) | Operators | Dual-model strategy: Gemma + MiniMax |
| [AGENT-COMPARISON.md](docs/AGENT-COMPARISON.md) | Operators | Claude Code vs. Hermes vs. ZeroClaw vs. OpenClaw |

### Deployment and Operations

| Page | What's there |
|------|--------------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production setup, monitoring, runbook |

### Security and Privacy

| Page | What's there |
|------|--------------|
| [docs/DATA_FLOW.md](docs/DATA_FLOW.md) | Data flow, cloud transmission (opt-in), threat model, defaults |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and disclosure policy |

---

## License

License: Apache 2.0 Dual License

See [LICENSE](LICENSE) for full terms.

---

Author: Jason Perlow | Questions? [Open an issue on GitHub](https://gitlab.com/argonautsystems/InvestorClaw/-/issues)

v2.6.0 | [Release Notes](RELEASE_NOTES.md) | Apache 2.0 License
