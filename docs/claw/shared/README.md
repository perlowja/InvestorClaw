# Claw-Family Shared Resources

Common patterns, architecture, and concepts across OpenClaw, ZeroClaw, and Hermes Agent.

## Architecture & Comparison

- **[Platform Comparison](./PLATFORM_COMPARISON.md)** — OpenClaw vs ZeroClaw feature matrix and key differences (Docker, sandbox, skill format, etc.)
- **[Feature Matrix](./FEATURE_MATRIX.md)** — Command availability across all platforms

## Skill Formats

InvestorClaw uses different skill formats depending on the Claw platform:

- **OpenClaw** — Uses `skill.json` manifest with tool definitions
- **ZeroClaw** — Uses `SKILL.md` knowledge document (open-skills pattern)
- **Hermes Agent** — Uses Python CLI directly via `pip install`

See individual platform guides for details.

## Local Inference & Offline Analysis

All Claw platforms support local Ollama/vLLM for on-device analysis (no API calls required).

- **[Local Inference Guide](./LOCAL_INFERENCE_GUIDE.md)** — Setup Ollama, llama-server, or vLLM for offline portfolio analysis
- **Platform-specific notes:**
  - **OpenClaw**: Use `.env` variables (`INVESTORCLAW_CONSULTATION_ENDPOINT`, etc.)
  - **ZeroClaw**: Docker sandbox blocks `localhost` — use `172.17.0.1:11434` (Docker bridge IP)
  - **Hermes Agent**: Uses `INVESTORCLAW_LOCAL_LLM_ENDPOINT` directly

## Common Configuration

All Claw platforms use environment variables for configuration:

```bash
# Market data APIs (optional)
FINNHUB_KEY=...
NEWSAPI_KEY=...
POLYGON_API_KEY=...

# LLM inference
INVESTORCLAW_OPERATIONAL_LLM=...
INVESTORCLAW_LOCAL_LLM_ENDPOINT=...
```

---

**Back to platform-specific guides**: [Claw Home](../README.md)
