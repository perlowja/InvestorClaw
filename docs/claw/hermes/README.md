# Hermes Agent — InvestorClaw Local Inference Setup

Deploy InvestorClaw with **local Ollama/vLLM** for on-device analysis (no API calls required).

Use Hermes 3.0 or any compatible LLM for portfolio analysis on any hardware (macOS, Linux, Windows with WSL).

---

## Quick Start (5 minutes)

### 1. Install InvestorClaw + Hermes Agent

```bash
curl -sSL https://gitlab.com/argonautsystems/InvestorClaw/-/raw/main/hermes/install.sh | bash
```

Installer:
- Clones InvestorClaw repo
- Sets up Python venv with dependencies
- Pulls Hermes 3.0 (8B quantized) via Ollama
- Creates `.env` with local LLM configuration

### 2. Activate Virtual Environment

```bash
source ~/.investorclaw/venv/bin/activate
```

### 3. Analyze Your Portfolio

```bash
investorclaw ask "What's in my portfolio?"
investorclaw refresh
```

---

## What You Get

- ✅ InvestorClaw running locally (no cloud API calls)
- ✅ Hermes 3.0 (8B, quantized for speed)
- ✅ Ollama backend for model serving
- ✅ Two-command deterministic surface available via CLI
- ✅ ~30-40 tokens/sec throughput
- ✅ Full portfolio analysis offline

---

## Configuration

### Models

The installer pre-configures **Hermes 3.0 (8B quantized)**:

```bash
INVESTORCLAW_LOCAL_LLM_MODEL=hermes3:8b-q4_K_M
INVESTORCLAW_LOCAL_LLM_ENDPOINT=http://localhost:11434
```

### Switch Models

To use a different model:

1. Pull it with Ollama:
```bash
ollama pull mistral:latest
```

2. Update `~/.investorclaw/.env`:
```bash
INVESTORCLAW_LOCAL_LLM_MODEL=mistral:latest
```

3. Restart InvestorClaw

### Market Data APIs (Optional)

```bash
FINNHUB_KEY=your_key
NEWSAPI_KEY=your_key
POLYGON_API_KEY=your_key
```

---

## Supported Models

| Model | Size | Speed | Quality | Notes |
|-------|------|-------|---------|-------|
| Hermes 3 (8B) | 6GB | ⚡⚡ Fast | ⭐⭐⭐⭐ Good | Default; balanced |
| Hermes 3 (70B) | 40GB | ⚡ Slower | ⭐⭐⭐⭐⭐ Excellent | High-end only |
| Mistral (7B) | 4GB | ⚡⚡⚡ Very fast | ⭐⭐⭐ OK | Lightweight |
| Llama 2 (70B) | 40GB | ⚡ Slower | ⭐⭐⭐⭐ Very good | Older but solid |

All models work with InvestorClaw's `ask` / `refresh` command set.

---

## Commands

The v2.5.0 InvestorClaw commands work locally:

```bash
investorclaw ask "What's in my portfolio?"
investorclaw ask "How am I doing?"
investorclaw ask "Show my bond exposure"
investorclaw refresh
```

`investorclaw ask` eagerly runs the required backend commands and narrates from the signed deterministic envelope.

---

## Troubleshooting

**"ollama: command not found"**: Install Ollama from https://ollama.ai

**"Connection refused at localhost:11434"**: Start Ollama: `ollama serve`

**Slow responses**: 
- Hermes Agent 8B is expected at ~30-40 tok/s on CPU
- Use GPU for 2-3x speedup (NVIDIA/AMD)
- Consider Mistral 7B for faster, lighter analysis

**Model not found**: Pull it: `ollama pull hermes3:8b-q4_K_M`

**Out of memory**: Use smaller model (Mistral 7B instead of Hermes Agent 70B)

---

## Advanced: vLLM for Speed

For faster inference on GPU, use vLLM instead of Ollama:

```bash
python -m vllm.entrypoints.openai_api_server \
  --model ~/.cache/huggingface/hub/models--meta--llama-2-70b-chat-hf \
  --quantization bitsandbytes \
  --port 8000 &

# Update .env
INVESTORCLAW_LOCAL_LLM_ENDPOINT=http://localhost:8000
```

---

## Learn More

- **[Local Inference Setup](../shared/LOCAL_INFERENCE_GUIDE.md)** — Deep dive into Ollama, llama-server, vLLM
- **[Architecture & Comparison](../shared/PLATFORM_COMPARISON.md)** — How Hermes Agent differs from OpenClaw and ZeroClaw
- **[Ollama Documentation](https://ollama.ai)** — Model management and performance tuning
- **[Hermes Agent Model Card](https://huggingface.co/NousResearch/Hermes Agent-3-Llama-3.1-8B)** — Model details and capabilities

---

**Next**:
- **Other Claw platforms?** → [Claw Home](../README.md)
- **Claude Code?** → [Claude Documentation](../../claude/README.md)
