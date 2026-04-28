# InvestorClaw — Dual-Model Architecture

**v2.1.4** | Understanding Narrative + Consultation layers | Two recommended production configs

---

## The Problem

InvestorClaw generates **two types of text**:

1. **Narrative** — Entertainment/commentary wrapping analysis results
   - Stonkmode personas (fictional TV finance characters)
   - Dr. Stonk financial education explanations
   - Contextual flavor text

2. **Consultation** — Synthesis of portfolio data into insights
   - Multi-factor analysis
   - Rebalancing recommendations
   - Risk assessment talking points

**Both are optional.** But using a dual-model approach optimizes cost and latency:
- **Narrative** → Smaller, faster model (Together.ai, xAI, Ollama)
- **Consultation** → Larger, more capable model (Google Gemini, local GPU)

---

## The Two Recommended Configs

### Config 1: **Together.ai (Budget-Optimized)** ⭐ Recommended for most users

**Narrative**: Together.ai MiniMax-M2.7  
**Consultation**: Local Ollama/llama-server or Together.ai Gemma-4-31B

```bash
# .env
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=<together_key>
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7

INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://your-gpu-host:8080  # OR Together.ai
INVESTORCLAW_CONSULTATION_MODEL=gemma-4-31B-it
```

**Why Together.ai?**
- ✅ Best price/performance ratio ($0.30/M tokens for narrative)
- ✅ MiniMax-M2.7 excellent for entertainment/commentary
- ✅ Works with local GPU for consultation (zero additional cloud spend)
- ✅ Tested on V8.1 harness: QC4=108 (highest quality score)

**When to choose**: Personal portfolios, cost-sensitive deployments, advisory firms

**Cost per 1M portfolios**: ~$0.30 (narrative only), or ~$5–20 if using cloud consultation

---

### Config 2: **Google Gemini (Premium-Optimized)** ⭐ Recommended for 1M+ context

**Narrative**: Google Gemini 3.1 Pro (1M context window!)  
**Consultation**: Local Ollama/llama-server or Gemini

```bash
# .env
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.generativeai.google.com/v1beta/openai/  # via OpenAI adapter
INVESTORCLAW_NARRATIVE_API_KEY=<google_api_key>
INVESTORCLAW_NARRATIVE_MODEL=gemini-3.1-pro

INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://your-gpu-host:8080  # OR Gemini
INVESTORCLAW_CONSULTATION_MODEL=gemma-4-31B-it
```

**Why Google Gemini?**
- ✅ 1M context window (can analyze massive portfolios + conversation history)
- ✅ Excellent reasoning for complex financial narratives
- ✅ Gemini 3.1 Pro: QC4=46 (excellent quality)
- ✅ Better long-form analysis than Together.ai

**When to choose**: Enterprise portfolios (500+ holdings), high-context sessions, complex narratives

**Cost per 1M portfolios**: ~$1–3 (Gemini is more expensive but higher quality)

---

## Comparison: Together.ai vs Google

| Dimension | Together.ai | Google Gemini |
|-----------|-------------|---------------|
| **Narrative Model** | MiniMax-M2.7 | Gemini 3.1 Pro |
| **Context Window** | 4K | **1M** |
| **Quality (QC4)** | 108 | 46 |
| **Cost per 1M** | **$0.30** | $1–3 |
| **Latency** | 1–2s | 2–4s |
| **Best For** | Smaller portfolios, entertainment | Large portfolios, complex analysis |
| **Local Fallback** | Yes (Ollama) | Yes (Ollama) |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ InvestorClaw Pipeline                                       │
└─────────────────────────────────────────────────────────────┘

1. Data Fetching
   └─→ yfinance / Finnhub / Polygon / FRED / NewsAPI

2. Analysis (Deterministic Python)
   └─→ Sharpe, beta, max drawdown, YTM, HHI, diversification
   └─→ Concentration, sector weights, news correlation
   └─→ Bond math (duration, convexity, FRED benchmarks)

3. Serialization
   └─→ Compact JSON output (2–5K tokens)

4. LLM Processing (Two Optional Layers)

   ┌─────────────────────────────────────┐
   │ NARRATIVE LAYER (Optional)          │
   │ ─────────────────────────────────   │
   │ Model: Together.ai MiniMax-M2.7     │ ← Config 1 (Budget)
   │ OR: Google Gemini 3.1 Pro           │ ← Config 2 (Premium)
   │                                     │
   │ Purpose: Entertainment/Commentary   │
   │ - Stonkmode personas                │
   │ - Dr. Stonk education               │
   │ - Contextual flavor text            │
   │                                     │
   │ Cost: Minimal ($0.30–1/M tokens)    │
   └─────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────┐
   │ CONSULTATION LAYER (Optional)       │
   │ ─────────────────────────────────   │
   │ Model: Local Ollama (free)          │ ← Best: 0 cost
   │ OR: Local llama-server (free)       │
   │ OR: Cloud Gemma-4-31B ($5–20/M)     │
   │                                     │
   │ Purpose: Portfolio Synthesis        │
   │ - Multi-factor analysis             │
   │ - Rebalancing suggestions           │
   │ - Risk assessment                   │
   │                                     │
   │ Cost: Varies (local=free, cloud=$)  │
   └─────────────────────────────────────┘
                    ↓
5. Output (Always Guardrailed)
   └─→ JSON + text with disclaimers + Dr. Stonk explanations
```

---

## Model Selection Matrix

**Choose Together.ai if:**
- ✅ Cost-conscious (narrative + local consultation = ~$0.30/query)
- ✅ Portfolio < 100 holdings
- ✅ Session context < 10K tokens
- ✅ Entertainment/Stonkmode matters (excellent for personas)
- ✅ Local GPU available (Ollama fallback for consultation)

**Choose Google Gemini if:**
- ✅ Portfolio > 500 holdings
- ✅ Long conversation history needed
- ✅ Complex analysis with full context retention
- ✅ Quality score matters more than cost (QC4=46 vs 108)
- ✅ Can spend $1–3 per query

---

## Hybrid Approach (Recommended Production)

**Best of both worlds:**

```bash
# Use Together.ai for narrative (cheap, fast, entertaining)
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=<together_key>
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7

# Use local GPU for consultation (free, private)
INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://your-gpu-host:8080
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
```

**Cost**: ~$0.30/narrative + $0 consultation (amortized GPU cost)  
**Latency**: 2–3s total  
**Quality**: Entertainment ✅ + Analysis ✅

---

## Why Two Models?

**Efficiency**: Different tasks require different models.

- **Narrative** is **repetitive, stateless**
  - Same commentary patterns for different portfolios
  - No need for large context window
  - Fast + cheap is better

- **Consultation** is **complex, stateful**
  - Needs to synthesize multiple data sources
  - Benefits from larger context
  - Quality matters more than speed

**By splitting, we:**
1. **Reduce cost** — Use cheaper model for narrative
2. **Reduce latency** — Can parallelize if needed
3. **Improve quality** — Right tool for each job
4. **Enable local execution** — Consultation stays private

---

## Setup Examples

### Example 1: Together.ai + Local GPU (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Start GPU service (if you have GPU)
ssh gpu-host "systemctl start llama-gemma4"

# Configure
cat > ~/.openclaw/workspace/skills/investorclaw/.env << 'EOF'
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.together.xyz/v1
INVESTORCLAW_NARRATIVE_API_KEY=<your_together_key>
INVESTORCLAW_NARRATIVE_MODEL=MiniMaxAI/MiniMax-M2.7

INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://192.0.2.96:8080
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
EOF

# Test
/portfolio holdings
/portfolio synthesize
```

### Example 2: Google Gemini Only (Simplest Cloud-Only)

```bash
cat > ~/.openclaw/workspace/skills/investorclaw/.env << 'EOF'
INVESTORCLAW_NARRATIVE_PROVIDER=openai_compat
INVESTORCLAW_NARRATIVE_ENDPOINT=https://api.generativeai.google.com/v1beta/openai/
INVESTORCLAW_NARRATIVE_API_KEY=<your_google_key>
INVESTORCLAW_NARRATIVE_MODEL=gemini-3.1-pro

# No consultation (local synthesis disabled)
INVESTORCLAW_CONSULTATION_ENABLED=false
EOF

# Test
/portfolio holdings
# Narrative only, no synthesis
```

### Example 3: Air-Gapped (No Cloud)

```bash
cat > ~/.openclaw/workspace/skills/investorclaw/.env << 'EOF'
INVESTORCLAW_NARRATIVE_PROVIDER=ollama
INVESTORCLAW_NARRATIVE_ENDPOINT=http://localhost:11434
INVESTORCLAW_NARRATIVE_MODEL=gemma4:e4b

INVESTORCLAW_CONSULTATION_ENABLED=true
INVESTORCLAW_CONSULTATION_ENDPOINT=http://localhost:8080
INVESTORCLAW_CONSULTATION_MODEL=gemma4-consult
EOF

# Start Ollama
ollama serve

# In another terminal, run commands
/portfolio holdings
/portfolio synthesize
```

---

## Troubleshooting

**Narrative never appears (stonkmode silent)**
- Check: Is `INVESTORCLAW_NARRATIVE_PROVIDER` set?
- Check: Is endpoint reachable? `curl https://api.together.xyz/v1/models`
- Check: Run `/portfolio stonkmode on` to activate state file

**Consultation endpoint unreachable**
- Disable: `INVESTORCLAW_CONSULTATION_ENABLED=false`
- Or: Start GPU service: `ssh gpu-host "systemctl start llama-gemma4"`

**Cost too high**
- Switch to Together.ai MiniMax (cheaper than Gemini)
- Use local Ollama for consultation (free)
- Disable narrative if you don't need Stonkmode

**Latency too high**
- Use Together.ai instead of Gemini (faster)
- Use local Ollama instead of cloud consultation
- Disable consultation layer if not needed

---

## See Also

- [CONFIGURATION.md](docs/CONFIGURATION.md) — Full env var reference
- [QUICKSTART.md](QUICKSTART.md) — Installation
- [FEATURES.md](FEATURES.md) — Capabilities overview
- [STONKMODE.md](docs/STONKMODE.md) — Entertainment mode details
- See `commands/optimize.py` and [COMMANDS.md](COMMANDS.md) § "Portfolio Optimization"

---

**Questions?** Open an issue: https://gitlab.com/argonautsystems/InvestorClaw/-/issues
