# Local Inference Engine Guide

## Overview

InvestorClaw supports multiple local inference engines for running LLMs on your hardware. This guide explains the differences, setup requirements, and troubleshooting for each engine.

## Quick Comparison

| Engine | Type | Port | Ease | API | Quirks | Recommend |
|--------|------|------|------|-----|--------|-----------|
| **llama-server** | CLI binary | 8080 | Medium | OpenAI ✅ | None | ⭐⭐⭐ |
| **LMStudio** | GUI App | 8000 | Easy | OpenAI (~) | Toggle required | ⭐⭐ |
| **Ollama** | CLI daemon | 11434 | Easy | Native | 4K context | ⭐⭐ |
| **vLLM** | Python lib | 8000 | Hard | OpenAI ✅ | Dev setup | ⭐ |

## Detailed Guides

### 1. llama-server (Recommended)

**Recommended for:** Production use, maximum compatibility, 131K context

**Setup:**
```bash
# macOS via Homebrew
brew install llama.cpp

# Start server with gemma-4
llama-server -m ~/models/gemma-4-E4B-it-Q6_K.gguf -ngl 99 --port 8080

# InvestorClaw config
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080
export INVESTORCLAW_CONSULTATION_MODEL=gemma-4-E4B-it-Q6_K
```

**Advantages:**
- Full OpenAI-compatible API
- 131K token context (vs Ollama 4K)
- Excellent performance on modern GPUs
- No external service dependencies

**Quirks:**
- None known — most compatible option

### 2. LMStudio

**Recommended for:** Users preferring GUI interface

**Setup:**
1. Download from https://lmstudio.ai
2. Launch LM Studio
3. **Settings > Developer > Enable API Server** (toggle must be ON!)
4. Load a model from the search tab
5. Go to Developer > Local Server
6. Click "Start Server"

**InvestorClaw config:**
```bash
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8000
export INVESTORCLAW_CONSULTATION_MODEL=gemma-4-9b-instruct
# (Use the exact model name shown in LM Studio)
```

**Advantages:**
- User-friendly GUI
- Model management via search
- Easy model switching

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| "Could not reach API" | Server not enabled | Settings > Developer > **Enable API Server toggle** |
| Connection refused | Wrong port | Verify port 8000 in Local Server settings |
| "No models available" | No model loaded | Load a model in main UI before starting server |
| HTTP 500 errors | Model not loaded | Ensure model shows in LM Studio UI before API calls |
| Empty responses | Model context exhausted | Use a smaller model or reduce max_tokens |

**Quirks:**
- Requires explicit "Enable API Server" toggle in Settings > Developer (not obvious!)
- Model name must match exactly what's shown in LM Studio UI
- Some model architectures may have subtle API differences
- Port 8000 (not 8080 or 11434!)

### 3. Ollama

**Recommended for:** Simple local inference, prefer daemon model

**Setup:**
```bash
# Install
brew install ollama

# Start daemon (runs in background)
ollama serve &

# Pull and run model
ollama pull gemma:7b

# InvestorClaw config
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
export INVESTORCLAW_CONSULTATION_MODEL=gemma:7b
```

**Advantages:**
- Simplest to get started
- Daemon runs in background
- Native /api/generate endpoint

**Quirks:**
- 4K token context (fixed)
- No API server mode toggle needed
- Uses custom /api/generate format (not OpenAI-compatible by default)

### 4. vLLM

**Recommended for:** Advanced users, high-performance requirements

**Setup:**
```bash
pip install vllm

# Start server
python -m vllm.entrypoints.openai.api_server \
  --model google/gemma-4-9b-instruct \
  --gpu-memory-utilization 0.9 \
  --tensor-parallel-size 1

# InvestorClaw config
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8000
export INVESTORCLAW_CONSULTATION_MODEL=google/gemma-4-9b-instruct
```

**Advantages:**
- Highest throughput
- Excellent for batch processing
- Full OpenAI API compatibility

**Quirks:**
- Requires Python dev environment
- Steeper learning curve
- GPU-specific setup

## Configuration Hierarchy

InvestorClaw uses intelligent fallbacks for local inference:

```
1. Check INVESTORCLAW_CONSULTATION_ENDPOINT/MODEL (explicit user config)
2. Check INVESTORCLAW_NARRATIVE_ENDPOINT/MODEL (stonkmode narration, optional)
3. Check INVESTORCLAW_STONKMODE_ENDPOINT/MODEL (legacy, backward compat)
4. Fall back to OPENCLAW_MODEL (if set)
5. Use built-in defaults (gemma4:e4b for Ollama, grok-3-fast for OpenAI)
```

## API Format Detection

InvestorClaw auto-detects the API format by probing in this order:

1. **Try `/api/tags`** → If responds:
   - Contains "object":"list" → llama-server (OpenAI-compatible)
   - No "object" field → Ollama (native format)

2. **Try `/v1/models`** → If responds → LMStudio or vLLM (OpenAI-compatible)

3. **Try `/health`** → If responds → Health check passes (OpenAI-compatible)

4. **Default** → Assume OpenAI-compatible (safest for unknown engines)

## Troubleshooting Matrix

| Symptom | Engine | Likely Cause | Fix |
|---------|--------|--------------|-----|
| Connection refused | Any | Server not running | Start the daemon/server |
| Port already in use | Any | Another app on port | Use different port, kill process |
| HTTP 400/422 | OpenAI-compat | Bad API format | Check request payload |
| HTTP 500 | LMStudio | Model not loaded | Load model in UI |
| Timeout | Any | GPU overloaded | Reduce concurrent requests |
| Empty response | Any | Model context full | Reduce max_tokens |
| Wrong answers | Any | Wrong model loaded | Verify model name |

## Performance Notes

**Context vs Speed Trade-off:**

- llama-server: 131K context @ ~64 tok/s
- Ollama: 4K context @ ~66 tok/s
- vLLM: 8K-32K context @ ~90+ tok/s (mode-dependent)

**VRAM Requirements:**

- gemma-4-9b-instruct: 12-16 GB
- qwen2.5:14b: 16-20 GB
- llama-2-70b-chat: 40+ GB (or quantized: 16-24 GB)

## Windows-Specific Configuration

### Network Access (Remote Machine or WSL)

If InvestorClaw is running on a different Windows machine or in WSL:

**LMStudio Network Binding:**
1. Go to **Settings > Developer > Local Server**
2. Change network binding from `127.0.0.1` to `0.0.0.0`
3. This allows access from other machines on the network
4. Restart the local server

**LMStudio CORS Configuration:**
1. Go to **Settings > Developer**
2. Enable **CORS** (Cross-Origin Resource Sharing)
3. This allows requests from remote origin (e.g., WSL container)

**Windows Firewall:**

PowerShell (run as Administrator):
```powershell
# Add LMStudio port to Windows Firewall
New-NetFirewallRule -DisplayName "LMStudio API" `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort 8000

# For llama-server (port 8080)
New-NetFirewallRule -DisplayName "llama-server API" `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort 8080

# For Ollama (port 11434)
New-NetFirewallRule -DisplayName "Ollama API" `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort 11434
```

**Or via Windows Defender Firewall GUI:**
1. Windows Defender Firewall > Allow an app through firewall
2. Click "Change settings"
3. Click "Allow another app"
4. Browse to LMStudio executable (usually `C:\Program Files\LMStudio\...`)
5. Select port 8000

### WSL Configuration

If running InvestorClaw in WSL with inference on Windows host:

**Discovery:**
```bash
# From WSL, find Windows host IP
cat /etc/resolv.conf
# Look for "nameserver X.X.X.X" (usually 172.31.x.x)

# Or use:
ip route show | grep default | awk '{print $3}'
```

**InvestorClaw Config (WSL):**
```bash
# Use Windows host IP instead of localhost
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://172.31.x.x:8000
export INVESTORCLAW_CONSULTATION_MODEL=gemma-4-9b-instruct
```

**LMStudio Settings (Windows):**
- Network binding: `0.0.0.0` (not 127.0.0.1)
- CORS: Enabled
- Port: 8000 (or your custom port)

### Common Windows Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Connection refused" (WSL→Windows) | Network binding to 127.0.0.1 | Change to 0.0.0.0 in LMStudio Settings |
| CORS errors | CORS not enabled | Enable CORS in LMStudio Settings > Developer |
| Firewall blocks port | Windows Defender blocking traffic | Add firewall exception for port 8000 (see above) |
| "No route to host" | WSL can't reach Windows host | Check IP from `/etc/resolv.conf`, verify firewall |
| "Timeout" on LMStudio API | Network binding or firewall | Check both 0.0.0.0 binding and firewall rule |

## Best Practices

1. **Use llama-server for production** — most compatible, best context
2. **Use LMStudio if you want GUI** — remember the "Enable API Server" toggle!
3. **Test `/health` or `/v1/models` before config** — verifies endpoint is reachable
4. **Monitor GPU memory** — reduce max_tokens if hitting limits
5. **Match model names exactly** — copy from engine UI to avoid mismatches
6. **Use quantized models** — Q6_K or Q8_0 for good quality/performance ratio
7. **For remote/WSL access:**
   - Set network binding to `0.0.0.0` (not 127.0.0.1)
   - Enable CORS in LMStudio
   - Add Windows firewall exceptions
   - Use correct host IP (not localhost)

## Getting Help

If inference fails:
1. Test endpoint manually: `curl http://localhost:PORT/health` or `/v1/models`
2. Check engine logs (usually in UI or stdout)
3. Verify model is loaded in the engine
4. Try a different model to isolate the issue
5. Refer to engine's documentation (llama.cpp, LM Studio, Ollama, vLLM)

## Environment Variables by Platform

### Claude Code
Claude Code uses Anthropic models by default. For local inference:

```bash
# Configure local LLM for Claude Code (optional)
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080
export INVESTORCLAW_CONSULTATION_MODEL=gemma-4-9b-instruct
```

**Note:** Claude Code can also use `/ic-llm-config` skill to configure local inference interactively.

---

### OpenClaw
```bash
# Consultation (primary analysis) LLM
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080
export INVESTORCLAW_CONSULTATION_MODEL=gemma-4-9b-instruct

# Narrative (stonkmode) LLM (optional, different model)
export INVESTORCLAW_NARRATIVE_ENDPOINT=...
export INVESTORCLAW_NARRATIVE_MODEL=...

# API authentication (if required)
export INVESTORCLAW_CONSULTATION_API_KEY=...
```

---

### ZeroClaw
**⚠️ Docker Sandbox Restriction:** localhost (127.0.0.1) is not accessible from inside the Docker container.

**Solution:** Use Docker bridge IP instead:

```bash
# Use Docker host IP, NOT localhost
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://172.17.0.1:11434
export INVESTORCLAW_CONSULTATION_MODEL=hermes3:8b-q4_K_M

# Or enable host networking in zeroclaw config:
# [runtime.docker]
# network = "host"  # Allows localhost access (less secure)
```

---

### Hermes Agent (Local CLI)
Hermes Agent is the local-inference CLI deployment, using Ollama directly.

```bash
# Primary inference engine (Hermes Agent default)
export INVESTORCLAW_LOCAL_LLM_ENDPOINT=http://localhost:11434
export INVESTORCLAW_LOCAL_LLM_MODEL=hermes3:8b-q4_K_M

# Optional: separate narration model
export INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:11434
export INVESTORCLAW_NARRATIVE_MODEL=hermes3:8b-q4_K_M

# API authentication (if required)
export INVESTORCLAW_LOCAL_LLM_API_KEY=...
```

**Note:** Hermes Agent uses `INVESTORCLAW_LOCAL_LLM_*` variables (not CONSULTATION), because it's the primary deployment path for local inference.

---

## Configuration Hierarchy

InvestorClaw uses intelligent fallbacks for local inference:

```
1. Platform-specific env vars (INVESTORCLAW_LOCAL_LLM_* for Hermes Agent, CONSULTATION_* for others)
2. INVESTORCLAW_NARRATIVE_ENDPOINT/MODEL (stonkmode narration, optional)
3. INVESTORCLAW_STONKMODE_ENDPOINT/MODEL (legacy, backward compat)
4. Fall back to OPENCLAW_MODEL (if set)
5. Use built-in defaults (hermes3:8b-q4_K_M for Ollama, grok-3-fast for OpenAI)
```

---

**Last Updated:** 2026-04-21  
**Status:** Production Ready
