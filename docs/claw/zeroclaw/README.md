# ZeroClaw — InvestorClaw Installation & Configuration

Deploy InvestorClaw as a **ZeroClaw skill** on ARM devices (Raspberry Pi 4/5) and minimal-resource environments.

---

## Quick Start (10 minutes)

### 1. Install InvestorClaw

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/zeroclaw/install.sh | bash
```

Installer creates: `~/investorclaw/` and configures zeroclaw

### 2. Configure ZeroClaw

Edit `~/.zeroclaw/config.toml` (critical settings):

```toml
[skills]
open_skills_enabled = false       # Prevent token overflow

[autonomy]
level = "full"                    # Allow non-interactive execution

[agent]
max_context_tokens = 131072       # Budget for InvestorClaw workflows

[runtime.docker]
image = "investorclaw-runtime:latest"  # Custom Python 3.13 + deps
network = "bridge"                     # Allow outbound for yfinance
```

Apply changes:
```bash
systemctl --user restart zeroclaw.service
```

### 3. Verify Installation

```bash
zeroclaw agent -m "investorclaw ask \"What's in my portfolio?\""
```

---

## What You Get

- ✅ InvestorClaw on ARM (Raspberry Pi, etc.)
- ✅ Skill format: `SKILL.md` (open-skills knowledge document)
- ✅ Docker-sandboxed execution
- ✅ Validated with: `openai/gpt-oss-120b` on Groq
- ✅ Full automation via ZeroClaw agent

---

## Configuration

### Environment Variables

Set in `~/.investorclaw/.env`:

```bash
# Market data APIs (optional)
FINNHUB_KEY=your_key_here
NEWSAPI_KEY=your_key_here
GROQ_API_KEY=your_groq_key_here

# LLM model
INVESTORCLAW_OPERATIONAL_LLM=openai/gpt-oss-120b
INVESTORCLAW_OPERATIONAL_PROVIDER=groq
```

### zeroclaw Config (Required)

`~/.zeroclaw/config.toml` must have:
- `open_skills_enabled = false` — prevent 96K token overflow from open-skills
- `max_context_tokens = 131072` — adequate budget for workflows
- `level = "full"` — allow shell tool execution over SSH
- `image = "investorclaw-runtime:latest"` — custom Docker image with Python + deps
- `network = "bridge"` — allow yfinance outbound calls

---

## Key Differences vs. OpenClaw

| Feature | OpenClaw | ZeroClaw |
|---------|----------|----------|
| Hardware | Any (Linux/macOS) | ARM (Pi, etc.) |
| Skill format | `skill.json` | `SKILL.md` |
| Sandbox | None | Docker (required for shell) |
| Docker image | N/A | `investorclaw-runtime:latest` |
| Validated model | xAI Grok | Groq `openai/gpt-oss-120b` |
| Max context | 200K+ | 131K (Docker budget) |

---

## Known Issues & Limitations

### Docker Sandbox Restrictions
- `backend = "none"` in config does NOT actually disable Docker in zeroclaw v0.6.9
- localhost (127.0.0.1) is not accessible from sandbox
- Use Docker bridge IP: `172.17.0.1:11434` for local Ollama

### Model Compatibility
- `grok-4-1-fast-reasoning` returns XML that zeroclaw v0.6.9 rejects
- Use `openai/gpt-oss-120b` (Groq) as validated fallback
- Test models thoroughly before production use

### SKILL.md Limitations
- Prompts are NOT injected into agent system prompt (zeroclaw v0.6.9 bug)
- Bootstrap prompt must include explicit command mappings (see `zeroclaw/SKILL.md`)

---

## Commands

The v2.5.0 InvestorClaw commands work via ZeroClaw's shell tool:

```bash
zeroclaw agent -m "investorclaw ask \"<question>\""
zeroclaw agent -m "investorclaw refresh"
```

Examples:
- `investorclaw ask "What's in my portfolio?"` — portfolio snapshot
- `investorclaw ask "How should I rebalance?"` — rebalancing analysis
- `investorclaw refresh` — force fresh prices/news/cache

See `zeroclaw/SKILL.md` for complete command mappings.

---

## Troubleshooting

**Command not found**: Restart zeroclaw service: `systemctl --user restart zeroclaw.service`

**Docker error**: Verify `investorclaw-runtime:latest` image exists: `docker images | grep investorclaw`

**Ollama not accessible**: Use Docker bridge IP `172.17.0.1:11434` instead of `localhost:11434`

**Context token error**: Increase `max_context_tokens` in `~/.zeroclaw/config.toml` to 131072+

---

## Learn More

- **[Architecture & Comparison](../shared/PLATFORM_COMPARISON.md)** — How ZeroClaw differs from OpenClaw and Hermes Agent
- **[Feature Matrix](../shared/FEATURE_MATRIX.md)** — Command support across platforms
- **[Local Inference Setup](../shared/LOCAL_INFERENCE_GUIDE.md)** — Ollama inside Docker sandbox
- **[ZeroClaw Official Docs](https://github.com/zeroclaw/zeroclaw)** — Full agent documentation
- **[Full Installation Guide](./ZEROCLAW_INSTALL.md)** — Detailed step-by-step setup

---

**Next**:
- **Other Claw platforms?** → [Claw Home](../README.md)
- **Claude Code?** → [Claude Documentation](../../claude/README.md)
