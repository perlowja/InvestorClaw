# Claw-Family Documentation

InvestorClaw for OpenClaw, ZeroClaw, and Hermes Agent.

**Claw-family** agents are open-source, self-hosted AI runtimes. InvestorClaw integrates as a **skill** (OpenClaw) or **knowledge document** (ZeroClaw) or **Python CLI** (Hermes Agent).

## OpenClaw

Deploy on general-purpose Linux/macOS workstations and servers.

- **[Quick Start](./openclaw/README.md)** — 5-minute setup with `openclaw agent`
- **[Skill Manifest Guide](./shared/PLATFORM_COMPARISON.md#openclaw)** — Understanding skill.json
- **[Installation & Configuration](../../openclaw/README.md)** — Full setup guide

## ZeroClaw

Deploy on ARM devices (Raspberry Pi 4/5) with minimal resources.

- **[Quick Start](./zeroclaw/README.md)** — 10-minute setup on Pi
- **[Installation & Configuration](./zeroclaw/ZEROCLAW_INSTALL.md)** — Detailed setup with Docker sandbox
- **[Skill Format (SKILL.md)](./shared/PLATFORM_COMPARISON.md#zeroclaw)** — Open-skills knowledge document pattern
- **[Known Issues](./zeroclaw/ZEROCLAW_INSTALL.md#known-issues)** — zeroclaw v0.6.9 quirks

## Hermes Agent (Local Inference)

Deploy with local Ollama/vLLM on any hardware (no API calls).

- **[Quick Start](./hermes/README.md)** — 5-minute setup with Ollama
- **[Local Inference Setup](./shared/LOCAL_INFERENCE_GUIDE.md)** — Ollama, llama-server, vLLM
- **[Installation & Configuration](../../hermes/README.md)** — Full setup guide

## Shared Resources

Architecture and patterns common to all Claw platforms.

- **[Platform Comparison](./shared/PLATFORM_COMPARISON.md)** — Feature matrix and architecture differences
- **[Feature Matrix](./shared/FEATURE_MATRIX.md)** — Command support across platforms
- **[Local Inference Guide](./shared/LOCAL_INFERENCE_GUIDE.md)** — Setting up Ollama/vLLM for offline analysis
- **[Skill Formats Explained](./shared/SKILL_FORMATS.md)** — SKILL.toml vs SKILL.md vs Python CLI

---

**Next**: Choose your platform or explore shared concepts:
- **Claude Code?** → [Claude Documentation](../claude/README.md)
- **General question?** → [InvestorClaw Home](../../README.md)
