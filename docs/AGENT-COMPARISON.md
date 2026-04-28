# Agentic CLI Apps Comparison

This guide compares four agentic apps used in this fleet: **Claude Code**, **Hermes Agent**, **ZeroClaw**, and **OpenClaw**.

Use it to answer a practical question first: is the app interactive or a daemon, and how should you run it?

## Summary

- **Claude Code** and **Hermes Agent** are interactive CLIs. You launch them, chat, and exit.
- Hermes Agent also offers an optional gateway daemon mode for chat-channel routing and cron.
- **ZeroClaw** and **OpenClaw** are daemons. They run as always-on gateway processes and serve an HTTP or WebSocket API.
- Other clients, such as Claude Code, chat UIs, and other agents, talk to ZeroClaw and OpenClaw.
- ZeroClaw and OpenClaw require a restart after a config change.
- When someone says "restart the agents," they almost always mean ZeroClaw and OpenClaw. They usually do not mean Claude Code or Hermes Agent.

## Comparison

|  | Claude Code | Hermes Agent | ZeroClaw | OpenClaw |
|---|---|---|---|---|
| Shape | Interactive CLI | Interactive CLI with optional daemon mode | Always-on daemon | Always-on daemon |
| Primary invocation | `claude` | `hermes` (TUI) | `zeroclaw daemon` | `openclaw gateway --port 18789` |
| Typical usage mode | You run it, chat, and exit. | You run it, chat, and exit. You can also talk to the gateway from Telegram, Discord, and similar channels. | Other clients call its gateway API. You do not usually run it directly. | Clients issue `openclaw agent …` calls or connect by WebSocket. You do not usually run it directly. |
| Optional daemon mode | No real equivalent | `hermes gateway start` drives chat-channel routing for Telegram, Discord, Slack, WhatsApp, Signal, and Email. It also drives the built-in cron scheduler. Install it as a service with `hermes gateway install` using a systemd user unit on Linux or a launchd agent on macOS. | The daemon is the primary mode. | The daemon is the primary mode. |
| Runtime persistence | No. Each run starts a fresh session. State lives through MCP or on-disk files. | No in TUI mode. Yes in gateway mode. | Yes. It stays on. | Yes. It stays on. |
| Model backend | Anthropic Claude (hosted, via API) | Native: OpenRouter, Nous Portal, Anthropic, Google Gemini, xAI, NVIDIA NIM, MiniMax, Ollama-Cloud, HuggingFace, plus `openai-codex` and `copilot`, and a long tail of OpenAI-compat adapters. Not native, but reachable through OpenRouter: Together, Groq, OpenAI direct API, Perplexity. Config-schema `custom_providers:` exists, but the CLI `--provider` argparse enum hardcodes the list, so custom providers are not CLI-invokable as of 2026-04-24. | Anything OpenAI-compatible, including OpenAI, Groq, Together, local llama-server, and vLLM, through provider plugins | Rich provider model under `models.providers.*` supporting OpenAI-completions, OpenAI-responses, Anthropic-messages, Google-generative-ai, GitHub Copilot, Bedrock, Ollama, Azure-OpenAI-responses |
| MCP support | Yes | Yes | Yes | Yes |
| Memory surface | MCP servers and session files | MCP, `~/.hermes/memories/` for local memory, a self-improvement loop, and FTS5 session search | MCP and `~/.zeroclaw/state/` for SQLite memory, audit trail, and knowledge graph | MCP and workspace-isolated state per agent |
| Config file(s) | `~/.claude/settings.json`, `~/.claude.json` (MCP), `~/.claude/mnemos-hooks.config` (hook env) | `~/.hermes/config.yaml`, `~/.hermes/agents_config.json`, `~/.hermes/cron/jobs.json` | `~/.zeroclaw/config.toml` with TOML sections such as `[providers]`, `[mcp]`, `[reliability]`, `[security]`, `[autonomy]`, and `[agent]`, plus many more. Also `~/.zeroclaw/.mcp.json`. | `~/.openclaw/openclaw.json` with a strict JSON schema including `models.providers.*`, `agents.defaults.model`, `mcpServers`, `auth.profiles`, and `secrets.providers` |
| Config change and restart | No. Relaunch the CLI. | No in TUI mode. Yes in gateway mode with `systemctl --user restart hermes-gateway`. | Yes. Run `sudo systemctl restart zeroclaw`. | Yes. Run `systemctl --user restart openclaw-gateway`. |
| Hooks and extensibility | Hook scripts on `SessionStart`, `UserPromptSubmit`, and `Stop`, plus plugins through `enabledPlugins` | Self-improving skill loop, skills directory under `~/.hermes/skills/`, and `optional-skills/` tree | Tool plugins, skill files under `.claude/skills/`, hooks, webhook audit, and workspace isolation | Agent plugins, skill trees under `.agents/skills/`, exec-approvals, channel bridges, and browser automation |
| License | Closed hosted. Claude Code CLI is OSS. | MIT (Nous Research) | Apache-2.0 (upstream `zeroclaw-labs/zeroclaw`) | Apache-2.0 |
| Lineage and family | Anthropic | Nous Research `hermes-agent`. This is a separate project, not part of the Claw family. | Claw family. This is the Rust runtime that NemoClaw and `nemoclawzero` or `nclawzero` build on. | Claw family. This is the TypeScript gateway and orchestrator. It shares API shape with NemoClaw and ZeroClaw. |

## Identify The Agent

Use these signals to tell which agent you are looking at.

- Port `42617` over HTTP on localhost or bound wide usually means the ZeroClaw daemon.
- Port `18789` or `18791` over WebSocket and localhost-bound usually means the OpenClaw gateway.
- No port usually means Claude Code or Hermes Agent TUI. Those run as in-process CLIs and keep state in `~/.claude/` or `~/.hermes/`.
- A systemd unit named `zeroclaw.service` means ZeroClaw at the system level.
- A systemd user unit named `openclaw-gateway.service` means OpenClaw.
- A systemd user unit named `hermes-gateway.service` means Hermes in gateway or daemon mode. This is rare.

## Shared Memory Through MCP

MCP, or Model Context Protocol, is the common denominator across all four agents.

You can register a single MNEMOS MCP server with all four agents. That gives them cross-agent shared memory.

Each agent uses the same MCP structure for `command`, `args`, and `env`.

Each agent stores that MCP config in a different file format:

- Claude Code uses JSON.
- OpenClaw uses JSON.
- Hermes Agent uses YAML.
- ZeroClaw uses a TOML block in its config.

## When To Use Each Agent

Use Claude Code for ad-hoc coding, debugging, and research.

Use Hermes Agent for a conversational agent that reaches chat channels such as Telegram, Discord, and Slack. Use it when you need scheduled tasks too.

Use ZeroClaw when other systems need to call an agent runtime through an API for automation, hooks, or continuous background work.

Use OpenClaw when you need a production gateway for multi-agent orchestration with isolated workspaces, approvals, and channel bridges.

## Running Them Together

All four can coexist on the same host.

They do not conflict because they bind different ports and keep isolated state directories.