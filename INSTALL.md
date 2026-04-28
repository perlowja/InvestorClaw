# InvestorClaw Installation Guide

v2.1.9 | All Platforms | One-Line Install

## Important Disclaimer

InvestorClaw is an educational portfolio analysis tool.

It is not a fiduciary advisor.

It does not provide investment advice.

It helps you have informed conversations with your financial advisor.

Always consult a qualified financial professional before you make investment decisions.

## Quick Install

Choose the install path that matches your runtime.

### Claude Code

Use this path if you run InvestorClaw in Claude Code. The Claude Code plugin is maintained in the separate InvestorClaude repo; install from there:

```text
/plugin marketplace add https://gitlab.com/argonautsystems/InvestorClaude.git
/plugin install investorclaw@investorclaude
```

This flow follows Anthropic's documented marketplace flow.

After official marketplace acceptance, use `/plugin install investorclaw@claude-plugins-official`.

After installation, ask InvestorClaude a portfolio question (`/investorclaw:ask "what's in my portfolio?"`).

You can also attach portfolio files and ask Claude to set up InvestorClaw.

Do not use manual `git clone` or Python package installation for Claude Code.

Benefits:

- Zero manual setup
- Natural-language portfolio analysis through InvestorClaude
- 3 automation skills
- Interactive artifacts
- Claude handles dependencies automatically

> Note:
> Dashboard support is in development and not included in the current default install.

### OpenClaw

Use this path if you run OpenClaw.

One-line install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform openclaw
```

Direct install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
```

Requirements:

- OpenClaw CLI

Benefits:

- Full OpenClaw integration
- Shell tool execution
- Multi-agent workflows

Install time: ~5 minutes

### Standalone CLI

Use this path if you want direct local development access.

One-line install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform standalone
```

Direct install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/standalone/install.sh | bash
```

Benefits:

- Direct Python CLI access
- No external dependencies
- Full control and development access
- Automated `uv` + venv + setup

Install time: ~3 minutes

### Hermes Agent

Use this path if you run InvestorClaw as a skill inside the Hermes Agent runtime.

Install InvestorClaw inside **Hermes Agent** ([github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)).

Hermes Agent is the CLI runtime.

Model choice is decoupled.

You can pair Hermes Agent with any provider it supports.

Supported cloud providers include OpenAI, Together, xAI, Anthropic, OpenRouter, and Nous Portal.

Supported local providers include Ollama, vLLM, llama-server, and LMStudio.

That local option supports offline use.

> Note:
> Hermes Agent is not the same product as the Hermes LLM family (Hermes 3, Hermes 4).
> Hermes LLM is a separate NousResearch model product.
> Hermes Agent can use a Hermes LLM as its backend.
> Hermes Agent can also use any other supported model.

One-line install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform hermes
```

Direct install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash
```

Benefits:

- Skill runs inside Hermes Agent (non-Anthropic agentic CLI)
- Any supported provider, either cloud or fully local
- Zero cloud dependency when paired with local backends (Ollama/vLLM/llama-server)

Install time: ~10-15 minutes (includes local model download if chosen)

### zeroclaw

Use this path if you run on Raspberry Pi.

One-line install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash -s -- --platform zeroclaw
```

Direct install:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/zeroclaw/install.sh | bash
```

Benefits:

- Optimized for Raspberry Pi
- Fixes zeroclaw v0.6.9 issues
- Automatic configuration
- Vendor dependency management

Fixes applied:

- Disables open-skills (prevents 96K token overflow)
- Increases context window to 131K tokens
- Enables full autonomy for skill execution
- Configures Docker sandbox properly

Install time: ~5 minutes

## Auto-Detection

Use the universal installer if you do not know which platform you have.

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/install.sh | bash
```

The installer detects these environments:

- OpenClaw on `PATH` and selects the OpenClaw installer
- Hermes Agent (`hermes`) on `PATH` and selects the Hermes Agent installer
- Raspberry Pi or ARM and selects the ZeroClaw installer
- Ollama, llama-server, or vLLM with no agent runtime and gives a standalone + local-backend hint
- No matching runtime and selects the standalone installer

## Runtime Matrix

| Runtime | Vendor | Install Time | Setup | Best For | Cloud Required |
|---|---|---|---|---|---|
| Claude Code | Anthropic | <1 min (click) | Automatic | Individual investors | Yes (Anthropic API) |
| OpenClaw | Open-source | ~5 min | Automatic | Teams, gateway routing, plugin ecosystem | Optional |
| ZeroClaw | Open-source (Rust) | ~5 min | Automatic | Raspberry Pi / ARM / edge | No |
| Hermes Agent | NousResearch | ~10-15 min | Automatic | Privacy-first + NousResearch stack | No (with local backend) |
| Nemoclaw | NousResearch (edge) | varies (Yocto image) | Manual | Low-power edge hardware | No |
| Standalone CLI | — | ~3 min | Automatic | Developers / dev-loop | No |

## Verify the Install

Run the command that matches your runtime.

```text
# Claude Code: use slash command
/investorclaw:investorclaw-setup
```

```bash
# OpenClaw: use agent
openclaw agent -m "investorclaw ask \"What's in my portfolio?\""
```

```bash
# Standalone / Hermes / zeroclaw:
source ~/.venv/bin/activate  # (or ./InvestorClaw/.venv/bin/activate)
investorclaw ask "What's in my portfolio?"
```

## Environment Setup

Each platform handles setup automatically.

Each installer does the following:

- Detects or installs `uv` when needed
- Creates an isolated Python venv
- Installs all dependencies
- Runs the portfolio setup wizard
- Creates a `.env` configuration template

No manual steps are required.

## Installation Locations

| Runtime | Skill / install directory | `.env` location |
|---|---|---|
| Claude Code | Plugin auto-managed | `~/.investorclaw/.env` |
| OpenClaw | `~/.openclaw/workspace/skills/investorclaw` | `$SKILL_DIR/.env` (skill-local, mode 600) |
| ZeroClaw | `~/investorclaw` | `$SKILL_DIR/.env` (skill-local, mode 600) |
| Hermes Agent | `~/InvestorClaw` (or `~/.hermes/skills/investorclaw` on container installs) | `$SKILL_DIR/.env` (skill-local, mode 600) |
| Nemoclaw | Yocto-image-managed | rootfs overlay (image-dependent) |
| Standalone CLI | `~/InvestorClaw` (or custom via `$INVESTORCLAW_HOME`) | `$INSTALL_DIR/.env` |

> Note:
> All skill-based installs keep the `.env` file inside the skill directory at `$SKILL_DIR/.env` with mode 600.
> If you have a legacy file at `~/.investorclaw/.env`, move it into the active `$SKILL_DIR`.
> You can also export the variables from your shell profile.

## Custom Installation Paths

Set environment variables before you run the installer.

```bash
# Standalone: custom installation directory
export INVESTORCLAW_HOME=/opt/investorclaw
curl -sSL ... | bash -s -- --platform standalone

# OpenClaw: custom skill directory
export INVESTORCLAW_SKILL_DIR=$HOME/.openclaw/workspace/skills/my-investorclaw
curl -sSL ... | bash -s -- --platform openclaw

# Any platform: custom portfolio directory
export INVESTORCLAW_PORTFOLIO_DIR=/data/portfolios
curl -sSL ... | bash
```

## First Run

### With a Portfolio CSV

Attach your broker CSV and ask InvestorClaw to analyze it.

```text
I have a portfolio CSV from [Schwab/Fidelity/Vanguard]. Analyze it.
[Attach CSV file]
```

Claude or the installed skill will do the following:

1. Stage the file to `~/portfolios/`
2. Run the setup wizard
3. Produce a holdings snapshot and portfolio analysis

### Without a Portfolio

Ask InvestorClaw to run setup.

```bash
investorclaw ask "Set up InvestorClaw and detect my portfolio files"
```

For Claude Code, ask InvestorClaude to run setup.

```text
Set up InvestorClaw and detect my portfolio files.
```

## Next Steps

After installation, do the following:

1. Add a portfolio by exporting a CSV from your broker and attaching it to chat.
2. Run a portfolio analysis with `investorclaw ask "Analyze my portfolio"`.
3. Force fresh data when needed with `investorclaw refresh`.
4. Configure API keys if you want them. InvestorClaw falls back to free `yfinance`.

> Note:
> Dashboard is in development and not shipped in the current default install. Ask dashboard questions through `investorclaw ask`; it returns the current deferral envelope where applicable.

## Troubleshooting

### Claude Code Plugin Did Not Appear

The Claude Code plugin lives in the InvestorClaude repo. Use Claude Code's plugin manager:

```text
/plugin marketplace add https://gitlab.com/argonautsystems/InvestorClaude.git
/plugin install investorclaw@investorclaude
```

Then refresh Claude Code.

Then ask a portfolio question via `/investorclaw:ask`.

### Standalone Installation Failed

Check the prerequisites first.

```bash
git --version
command -v curl
```

If that path still fails, try the standalone development setup.

```bash
git clone https://gitlab.com/argonautsystems/InvestorClaw.git
cd InvestorClaw
bash ./bin/setup-orchestrator
```

### `investorclaw` Command Not Found

Activate the venv.

```bash
source ~/.venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

### zeroclaw Issues

Check whether the config was updated.

```bash
cat ~/.zeroclaw/config.toml | grep -E 'open_skills|max_context|level|backend'
```

Restore from backup if needed.

```bash
cp ~/.zeroclaw/config.toml.backup.* ~/.zeroclaw/config.toml
```

## Documentation

- [QUICKSTART.md](QUICKSTART.md)
- [InvestorClaude README](https://gitlab.com/argonautsystems/InvestorClaude/-/blob/main/README.md)
- [openclaw/README.md](openclaw/README.md)
- [docs/ARCHITECTURE_INDEX.md](docs/ARCHITECTURE_INDEX.md)
- [FEATURES.md](FEATURES.md)
- [COMMANDS.md](COMMANDS.md)

Questions? Open an issue on [GitHub](https://gitlab.com/argonautsystems/InvestorClaw/-/issues).
