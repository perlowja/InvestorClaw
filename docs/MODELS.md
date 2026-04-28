# InvestorClaw LLM Model Configuration (v2.1)

Portfolio analysis using two recommended cloud providers with optional local consultative layer.

---

## Narrative Models (Primary Analysis Engine)

Your choice of provider determines narrative quality and context window.

### Option 1: Google Gemini 2.5 Flash (RECOMMENDED)

**Best for:** Higher context (1M tokens), excellent financial reasoning, enterprise support.

```json
{
  "provider": "google",
  "narrative_model": "google/gemini-2.5-flash",
  "context": "1M tokens",
  "cost": "~$10-20/month",
  "setup": "https://ai.google.dev"
}
```

**When to choose:**
- Need larger portfolios analyzed (1000+ positions)
- Require enterprise Gemini 3.1 Pro support
- Prefer Google infrastructure

---

### Option 2: Together AI MiniMax (Fast Alternative)

**Best for:** Speed-optimized analysis, lower cost, sufficient context for most portfolios.

```json
{
  "provider": "together",
  "narrative_model": "together/MiniMaxAI/MiniMax-M2.7",
  "context": "128K tokens",
  "cost": "~$10-20/month",
  "setup": "https://www.together.ai"
}
```

**When to choose:**
- Prefer speed over maximum context
- Analyzing typical retail portfolios (<500 positions)
- Want competitive pricing

---

## Consultative Models (Refinement Layer)

Optional second-stage synthesis. Refines narrative output before presentation.

### Mode 1: Cloud Gemma4 (Default)

Uses cloud provider's gemma4 model (same provider as narrative).

**Setup:**
- No additional configuration needed
- Uses same API key as narrative
- Included in narrative provider cost

**When to use:**
- First time setup (simplest)
- Cloud-only deployment
- Trust provider infrastructure

### Mode 2: Hybrid (Local gemma4-consult)

Run local gemma4-consult model via your choice of inference engine.

**Inference Engine Options:**

| Engine | Best For | Setup | Performance |
|--------|----------|-------|-------------|
| **Ollama** | Simplicity, macOS/Linux | Easiest (1 command) | ~30-40 tok/s |
| **llama.cpp** | Production, max context | Medium (download model) | ~60-70 tok/s |
| **LMStudio** | GUI preference, model switching | Easy (desktop app) | ~40-50 tok/s |
| **vLLM** | Max throughput, GPU | Harder (Python setup) | ~90+ tok/s |

**Setup Example (Ollama):**
```bash
# 1. Install Ollama
brew install ollama  # macOS

# 2. Pull gemma4-consult
ollama pull gemma4-consult

# 3. Start daemon
ollama serve &

# 4. Configure InvestorClaw
export INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:11434
export INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

**When to use:**
- Need full data privacy (nothing leaves your machine)
- Have GPU available for faster inference
- Analyzing sensitive financial data
- Custom model fine-tuning

---

## Configuration Examples

### Cloud Only (Simplest)
```json
{
  "narrative": {
    "provider": "google",
    "model": "gemini-2.5-flash",
    "api_key": "YOUR_GOOGLE_API_KEY"
  },
  "consultation": {
    "mode": "cloud",
    "model": "gemma4"
  }
}
```

### Hybrid (Local Consultative)
```json
{
  "narrative": {
    "provider": "google",
    "model": "gemini-2.5-flash",
    "api_key": "YOUR_GOOGLE_API_KEY"
  },
  "consultation": {
    "mode": "hybrid",
    "model": "gemma4-consult",
    "inference_system": "ollama",
    "endpoint": "http://localhost:11434"
  }
}
```

---

## Setup Wizard Flow (v2.1)

Run `investorclaw setup` for interactive configuration:

1. **Choose Narrative Provider**
   - Google Gemini 2.5 Flash (recommended)
   - Together AI MiniMax

2. **Enter API Key**
   - Get from provider's console
   - Stored securely in `~/.investorclaw/`

3. **Choose Consultative Mode**
   - Cloud (simple, default)
   - Hybrid (local + cloud narrative)

4. **(If Hybrid) Choose Inference Engine**
   - Ollama
   - llama.cpp
   - LMStudio
   - vLLM

5. **(If Hybrid) Configure Endpoint**
   - Ollama: `http://localhost:11434`
   - llama.cpp: `http://localhost:8080`
   - LMStudio: `http://localhost:8000`
   - vLLM: `http://localhost:8000`

---

## Cost Breakdown

| Config | Narrative | Consultative | Total |
|--------|-----------|--------------|-------|
| Cloud Only (Google) | $10-20/mo | Included | $10-20/mo |
| Cloud Only (Together) | $10-20/mo | Included | $10-20/mo |
| Hybrid (Google + local) | $10-20/mo | Free (hardware) | $10-20/mo + GPU |
| Hybrid (Together + local) | $10-20/mo | Free (hardware) | $10-20/mo + GPU |

---

## Supported Narrative Models (By Provider)

### Google
- `gemini-2.5-flash` (recommended for most users)
- `gemini-3.1-pro-preview` (enterprise tier, if available)

### Together AI
- `together/MiniMaxAI/MiniMax-M2.7` (recommended)

---

## Supported Consultative Models

**Cloud:**
- `gemma4` (via Google or Together AI)

**Local:**
- `gemma4-consult` (via Ollama, llama.cpp, LMStudio, or vLLM)

---

## Frequently Asked Questions

**Q: Which provider should I choose?**
A: Start with Google Gemini 2.5 Flash for maximum context. If you prefer speed and have typical portfolios, use Together AI MiniMax.

**Q: Do I need the consultative layer?**
A: No. Cloud mode uses only the narrative provider. Consultative is optional for advanced synthesis.

**Q: Can I switch providers later?**
A: Yes. Run `investorclaw setup` again anytime.

**Q: What if I want fully offline analysis?**
A: Use hybrid mode with local gemma4-consult. Narrative still uses cloud (unless you implement full local model).

---

See [setup/setup_wizard.py](../setup/setup_wizard.py) for interactive configuration.
