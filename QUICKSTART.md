# InvestorClaw Quick Start

v2.1.9

Install InvestorClaw and run it in about 5 minutes.

## Important Disclaimer

InvestorClaw is an educational portfolio analysis tool.

It is not a fiduciary advisor.

It does not provide investment advice.

It helps you have informed conversations with your financial advisor.

> Warning: Always consult a qualified financial professional before making investment decisions.

## Choose a Platform

InvestorClaw runs as a skill inside five agent runtimes.

It also runs as a standalone Python CLI for development use.

Choose the platform that fits your workflow.

| Runtime | Vendor | Best for |
|---|---|---|
| Claude Code | Anthropic | Individual investors, fastest start |
| OpenClaw | Open-source | Teams, gateway routing, plugin ecosystem |
| ZeroClaw | Open-source (Rust) | Raspberry Pi / ARM / edge |
| Hermes Agent | NousResearch ([github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)) | Privacy-first, NousResearch stack, fully local with Ollama/vLLM |
| Nemoclaw | NousResearch (edge) | Low-power edge hardware (Yocto-based `nclawzero` distro) |
| Standalone CLI | — | Developers / offline use without an agent runtime |

## Claude Code

Claude Code is the easiest and most integrated option.

Use Claude Code's documented marketplace flow.

```text
/plugin marketplace add https://gitlab.com/argonautsystems/InvestorClaw.git
/plugin install investorclaw@investorclaw
```

After official Anthropic marketplace acceptance, use this command:

```text
/plugin install investorclaw@claude-plugins-official
```

Run `/investorclaw:investorclaw-setup` next.

You can also attach broker files and ask Claude to set up InvestorClaw.

Do not clone this repo for Claude Code.

Do not run Python dependency installers for Claude Code.

The plugin setup skill owns that flow.

See [InvestorClaude README](https://gitlab.com/argonautsystems/InvestorClaude/-/blob/main/README.md) for the full Claude Code guide.

## OpenClaw

OpenClaw is the right choice if you use OpenClaw already.

Run this installer:

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/openclaw/install.sh | bash
```

The installer does these steps:

1. It checks prerequisites such as `git` and the OpenClaw CLI.
2. It clones the repository to `~/.openclaw/workspace/skills/investorclaw`.
3. It creates `.env` configuration.
4. It creates the `~/portfolios` directory.

The install takes about 2 minutes on standard broadband.

Ask InvestorClaw to set up next:

```bash
openclaw agent -m "investorclaw ask \"Set up InvestorClaw and detect my portfolio files\""
```

See [openclaw/README.md](openclaw/README.md) for the full OpenClaw guide.

## Standalone CLI

Use the standalone CLI for local development or scripting.

### Clone the repository

```bash
git clone https://gitlab.com/argonautsystems/InvestorClaw.git
cd InvestorClaw
```

### Run setup

Run the setup orchestrator:

```bash
bash ./bin/setup-orchestrator
```

The orchestrator does these steps automatically:

- Detects or installs `uv`
- Creates an isolated Python virtual environment
- Installs all dependencies
- Runs the portfolio setup wizard
- Verifies that everything works

The first setup takes about 3 minutes.

That time includes downloading `uv`, syncing dependencies, and running the wizard.

### Activate the environment and use commands

After setup completes, activate the environment:

```bash
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate`.

Then run commands directly:

```bash
investorclaw ask "What's in my portfolio?"
investorclaw ask "How am I doing?"
investorclaw refresh
```

> Note: The dashboard is in development for a later release. Ask dashboard questions through `investorclaw ask`; it returns the current deferral envelope where applicable.

### Platform support

| Platform | Support |
|---|---|
| macOS | Intel + Apple Silicon |
| Linux | Ubuntu, Debian, etc. |
| Windows | via WSL2 |

See [bin/README.md](bin/README.md) for more details.

## First Run

Start by configuring optional API keys.

Then add a portfolio file.

Then run commands.

### Configure optional API keys

Edit `~/.investorclaw/.env` if you want API-backed features.

InvestorClaw falls back to `yfinance` automatically.

```bash
FINNHUB_KEY=pk_...      # Real-time quotes & analyst ratings
NEWSAPI_KEY=...         # Portfolio news correlation
FRED_API_KEY=...        # Bond benchmarks
```

See [CONFIGURATION.md](CONFIGURATION.md) for the complete reference.

### Add a portfolio

Export holdings from your broker.

CSV is the preferred format.

| Broker | Export path |
|---|---|
| Schwab | Accounts → Positions → Export CSV |
| Fidelity | NetBenefits → Investments → Download CSV |
| Vanguard | My Accounts → Download Holdings (CSV) |
| UBS | Wealth Management → Holdings → Export CSV |

InvestorClaw also supports XLS, XLSX, and PDF files.

It auto-converts XLS and XLSX files.

It extracts tables from broker statement PDFs.

Place your file in `~/portfolios/`.

You can also use the sample file:

```bash
cp docs/samples/sample_portfolio.csv ~/portfolios/
```

### Run commands

```text
investorclaw ask "What's in my portfolio?"
investorclaw ask "How am I doing?"
investorclaw ask "Show my bond exposure"
investorclaw refresh
```

Use these prompts for these tasks:

| Prompt | Purpose |
|---|---|
| `investorclaw ask "Set up InvestorClaw"` | First-time portfolio discovery |
| `investorclaw ask "What's in my portfolio?"` | Holdings snapshot with live prices |
| `investorclaw ask "How am I doing?"` | Performance analysis |
| `investorclaw ask "Show my bond exposure"` | Bond analytics |
| `investorclaw ask "Analyze my portfolio"` | Multi-factor portfolio analysis |

## Natural Language Queries

You can ask InvestorClaw questions in plain English.

You do not need to memorize slash commands.

| Ask this... | Runs |
|---|---|
| "What's in my portfolio?" | `investorclaw ask` |
| "How am I doing?" | `investorclaw ask` |
| "Am I beating the market?" | `investorclaw ask` |
| "Show my bond exposure" | `investorclaw ask` |
| "What does Wall Street think?" | `investorclaw ask` |
| "Any news on my stocks?" | `investorclaw ask` |
| "Analyze my portfolio" | `investorclaw ask` |
| "How should I rebalance?" | `investorclaw ask` |
| "Tell me about NVDA" | `investorclaw ask` |
| "Generate a report" | `investorclaw ask` |

Follow-up questions also work.

After any command, you can ask questions such as "what does that mean?", "why is my beta high?", or "explain duration".

The agent answers in plain English.

It does not run another command for those follow-up explanations.

### Choose an interface

| Interface | Best for |
|---|---|
| Natural language | Exploring, follow-ups, wanting explanation with data, casual interaction |
| Refresh | Force fresh prices/news/cache with `investorclaw refresh` |
| Dashboard | Visual charts + ongoing monitoring are deferred. Ask dashboard questions through `investorclaw ask` for the canonical deferral envelope. |

> Note: The dashboard is deferred. The PWA is still in development.

## Default Settings

InvestorClaw starts in educational mode.

It is configured to help you learn as you go.

### Dr. Stonk Financial Education

Dr. Stonk is on by default.

Every output includes a Dr. Stonk Box with footnoted explanations of financial terms.

```text
🖖 Dr. Stonk (From the planet Hephaestus) — Logical Explanations
═══════════════════════════════════════════════════════════════════

[1] Sharpe Ratio: A most logical metric for measuring risk-adjusted returns...
[2] Beta: A coefficient measuring systematic market correlation...
```

Disable it by setting `INVESTORCLAW_DR_STONK_DISABLED=true` in `.env`.

### Verbose Output

Verbose output is on by default.

Analysis commands include full detail.

That detail includes these items:

- Complete metrics such as Sharpe ratio, beta, volatility, and correlation matrix
- Concentration analysis with HHI scoring
- Term definitions and explanations
- Risk assessment details

Disable it by setting `INVESTORCLAW_VERBOSE_DISABLED=true` in `.env`.

### Disable educational defaults

You can disable either setting after you get comfortable with the concepts.

```bash
echo "INVESTORCLAW_DR_STONK_DISABLED=true" >> ~/.investorclaw/.env
echo "INVESTORCLAW_VERBOSE_DISABLED=true" >> ~/.investorclaw/.env
investorclaw ask "What's in my portfolio?"
```

The last command gives you a compact view.

Ignore `--verbose` for CLI parsing.

## Standalone Python CLI

After you run `bash ./bin/setup-orchestrator`, use the installed console script for standalone development.

```bash
source .venv/bin/activate
investorclaw ask "Set up InvestorClaw and detect my portfolio files"
investorclaw ask "What's in my portfolio?"
investorclaw ask "How am I doing?"
investorclaw ask "Show my bond exposure"
investorclaw refresh
```

Inside OpenClaw, use `/portfolio ask "<question>"` or `/portfolio refresh`.

In a direct shell, use `investorclaw ask "<question>"` after standalone setup.

## Sample Portfolio

A sample 50-holding portfolio is included at `docs/samples/sample_portfolio.csv`.

Use it for testing.

```bash
cp docs/samples/sample_portfolio.csv ~/portfolios/
/investorclaw:ic-setup
/investorclaw:ic-holdings
```

This run takes about 5 seconds.

That time covers live quotes, concentration calculations, and rendering.

## Learn More

Use these docs for the next steps:

- [COMMANDS.md](COMMANDS.md) for all commands
- [CONFIGURATION.md](CONFIGURATION.md) for configuration
- [FEATURES.md](FEATURES.md) for features and capabilities
- [DEPLOYMENT.md](DEPLOYMENT.md) for portfolio optimization
- [docs/STONKMODE.md](docs/STONKMODE.md) for Stonkmode entertainment
- [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- [MODELS.md](MODELS.md) for models and benchmarks

## Troubleshooting

### "Portfolio files not found"

Run `/investorclaw:ic-setup`.

That command discovers CSV, Excel, and PDF files in `~/portfolios/`.

### "No API keys configured"

API keys are optional.

InvestorClaw falls back to `yfinance`.

Add keys in `.env` if you want analyst ratings or news.

### "Update available"

Run this command:

```text
/investorclaw:ic-check-updates --install
```

You can also skip update checks by adding `INVESTORCLAW_SKIP_UPDATE_CHECK=true`.

See [CONFIGURATION.md](CONFIGURATION.md) and [DEPLOYMENT.md](DEPLOYMENT.md) for more details.

## Questions

Open an issue at [github.com/argonautsystems/InvestorClaw/issues](https://gitlab.com/argonautsystems/InvestorClaw/-/issues).
