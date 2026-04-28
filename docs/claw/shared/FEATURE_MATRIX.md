# InvestorClaw Feature Matrix

Complete feature availability matrix for all five InvestorClaw deployment paths: Claude Code, OpenClaw, ZeroClaw, Hermes Agent, and Standalone CLI.

---

## Portfolio Analysis (Core Features)

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|---|
| **Holdings snapshot** | ✅ | ✅ | ✅ | ✅ | Current positions, live prices, concentration |
| **Performance metrics** | ✅ | ✅ | ✅ | ✅ | Sharpe ratio, beta, max drawdown, recovery |
| **Bond analytics** | ✅ | ✅ | ✅ | ✅ | YTM, duration, credit quality, ladder |
| **Analyst consensus** | ✅ | ✅ | ✅ | ✅ | Wall Street ratings & price targets |
| **News sentiment** | ✅ | ✅ | ✅ | ✅ | Headlines + correlation to holdings |
| **Multi-factor synthesis** | ✅ | ✅ | ✅ | ✅ | Combined insights across all dimensions |
| **Portfolio optimization** | ✅ | ✅ | ✅ | ✅ | Rebalancing suggestions (educational) |
| **Single-ticker lookup** | ✅ | ✅ | ✅ | ✅ | Deep dive on any holding |
| **CSV export** | ✅ | ✅ | ✅ | ✅ | Holdings + metrics to CSV |
| **Excel export** | ✅ | ✅ | ✅ | ✅ | Holdings + metrics to XLSX |
| **EOD HTML report** | ✅ | ✅ | ✅ | ✅ | Email-ready daily summary |
| **Stonkmode narration** | ✅ | ✅ | ✅ | ✅ | Comedy mode with finance personas |

---

## Presentation & Visualization

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|---|
| **Interactive dashboard** | ✅ | ❌ | ❌ | ❌ | Plotly charts (pie, sectors, bond ladder, simulator) |
| **Pie chart** | ✅ | ❌ | ❌ | ❌ | Equity/bond/cash allocation |
| **Sector breakdown** | ✅ | ❌ | ❌ | ❌ | Top 10 holdings by sector (clickable) |
| **Bond maturity ladder** | ✅ | ❌ | ❌ | ❌ | Market value by maturity year |
| **Sparklines** | ✅ | ❌ | ❌ | ❌ | 60-point performance per holding |
| **Rebalancing simulator** | ✅ | ❌ | ❌ | ❌ | Drag sliders to see allocation changes |
| **PDF export** | ✅ | ❌ | ❌ | ❌ | Dashboard → PDF via browser print |
| **Conversation history** | ✅ | ❌ | ❌ | ❌ | Multi-turn Q&A within same context |

---

## Data Input & Processing

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|---|
| **CSV import** | ✅ | ✅ | ✅ | ✅ | Primary format (Schwab, Fidelity, Vanguard, UBS) |
| **XLS/XLSX import** | ✅ | ✅ | ✅ | ✅ | Auto-converted to internal format |
| **PDF import** | ✅ | ✅ | ✅ | ✅ | Broker statements (table extraction) |
| **Vision extraction** | ✅ | ❌ | ❌ | ❌ | Screenshot/PDF of broker statement → auto-extracted CSV |
| **Multi-file consolidation** | ✅ | ❌ | ❌ | ❌ | Multiple broker CSVs in one turn → merged portfolio |
| **Automatic broker detection** | ✅ | ✅ | ✅ | ✅ | Schwab, Fidelity, Vanguard, UBS format recognition |
| **PII scrubbing** | ✅ | ✅ | ✅ | ✅ | Account numbers, SSNs removed automatically |

---

## LLM & Inference

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|---|
| **Operational LLM** | Claude (Haiku/Sonnet) | MiniMax-M2.7 or Gemini | MiniMax-M2.7 or Gemini | Local (Hermes 3, Mistral, Llama) | Primary analysis engine |
| **Narrative LLM** (stonkmode) | Claude | Together AI or Google (cloud) | Together AI or Google (cloud) | Local LLM | Always cloud/local; requires model or API key |
| **Consultative LLM** (enrichment) | N/A | Local gemma4-consult + cloud fallback | Local gemma4-consult + cloud fallback | Integrated with Narrative | **Required for narrative refinement** |

### Recommended Cloud Providers (Narrative + Consultative)

#### Provider 1: Together AI
| Component | Model | Notes |
|-----------|-------|-------|
| Narrative | `together/MiniMaxAI/MiniMax-M2.7` | QC4=108; best price/performance |
| Consultative (cloud) | `gemma4` (via Together) | Fallback when local unavailable |
| API Key | `TOGETHER_API_KEY` | Required in setup |

#### Provider 2: Google
| Component | Model (Standard) | Model (Enterprise) | Notes |
|-----------|---|---|---|
| Narrative | `google/gemini-2.5-flash` | `google/gemini-3.1-pro-preview` | Flash: 1M ctx; Pro: 1M ctx, higher quality |
| Consultative (cloud) | `gemma4` (via Google) | `gemma4` (via Google) | Fallback when local unavailable |
| API Key | `GOOGLE_API_KEY` | `GOOGLE_API_KEY` | Required in setup |

### Optional: Hybrid Mode (Local Consultative Enrichment)
| Component | Model | Infrastructure |
|-----------|-------|---|
| Narrative | Same cloud provider above | Cloud (required) |
| Consultative (local) | `gemma4-consult` | Ollama / llama-server / LMStudio (user-configured by setup wizard) |

### Configuration
| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|---|
| **Setup wizard** | ✅ | ✅ | ✅ | ✅ | Requests API keys and hybrid mode preference |
| **Disable narration** | ✅ | ✅ | ✅ | ✅ | Output Python computations only (no narrative) |
| **Verification layer** | ✅ Optional | ✅ Optional | ✅ Optional | ✅ Optional | HMAC fingerprinting for consultative synthesis |

---

## Data Privacy & Security

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|---|
| **Data stays local by default** | ✅ | ✅ | ✅ | ✅ Full | No transmission unless configured |
| **PII protection** | ✅ | ✅ | ✅ | ✅ | Account numbers never transmitted |
| **HTTPS encryption** | ✅ | ✅ | ✅ | ✅ | All external API calls (yfinance, Finnhub, etc.) |
| **HMAC fingerprinting** | ✅ Optional | ✅ | ✅ | ✅ Optional | Synthesis integrity verification |
| **File permissions** | ✅ | ✅ | ✅ | ✅ | .env and .hmac files chmod 0o600 |
| **GPG signature verification** | ✅ | ✅ | ✅ | ✅ | Auto-updater verifies release tags |
| **Trusted provider list** | ✅ | ✅ | ✅ | ✅ Local | Together, Groq, OpenAI, Google (no untrusted endpoints) |
| **Supply chain protection** | ✅ | ✅ | ✅ | ✅ | git HTTPS, 2FA on GitHub/GitLab |

---

## Configuration & Customization

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|
| **API key configuration** | Optional | Optional | Optional | Finnhub, NewsAPI, Polygon, Alpha Vantage, FRED |
| **Environment variables** | Minimal | Extensive | Extensive | .env file for provider, model, endpoint config |
| **Interactive setup wizard** | ✅ | ✅ | ✅ | Guided portfolio discovery and configuration |
| **Risk profile calibration** | ✅ | ✅ | ✅ | Set investor goals, guardrail strictness |
| **Deployment mode** | N/A | ✅ | ✅ | Single investor vs. FA professional |
| **Guardrail relaxation** | Standard | ✅ Optional | ✅ Optional | FA professional mode can relax educational guardrails |
| **Stateless by default** | ✅ | ✅ | ✅ | No persistent session data |

---

## Data Sources (All Platforms Support These)

| Data Source | Claude Code | OpenClaw | ZeroClaw | Pricing | Notes |
|---|---|---|---|---|---|
| **yfinance** | ✅ | ✅ | ✅ | Free, unlimited | Default (always works) |
| **Finnhub** | ✅ | ✅ | ✅ | Free (60 req/min) | Real-time quotes, analyst ratings |
| **NewsAPI** | ✅ | ✅ | ✅ | Free (100 req/day) | News correlation |
| **Polygon/Massive** | ✅ | ✅ | ✅ | Paid | Premium real-time OHLCV |
| **Alpha Vantage** | ✅ | ✅ | ✅ | Free (25 req/day) | Supplemental EOD + earnings |
| **FRED** | ✅ | ✅ | ✅ | Free (120 req/min) | Treasury & TIPS benchmarks |

---

## Narrative Layer (LLM Provider)

| Option | Claude Code | OpenClaw | ZeroClaw | Cost | Notes |
|---|---|---|---|---|---|
| **Anthropic (Haiku/Sonnet)** | ✅ Default | ❌ | ❌ | $0.05–$2.00/mo | Claude Code default |
| **xAI / Grok (4.1 Fast Reasoning)** | ❌ | ✅ Default | ⚠️ | Free tier / paid | OpenClaw default; ZeroClaw: v0.6.9 rejects XML output |
| **Groq (openai/gpt-oss-120b)** | ❌ | ✅ | ✅ Default | Free tier | ZeroClaw validated model |
| **Local Ollama** | ✅ Optional | ✅ | ⚠️ | Free (hardware) | llama-server or Ollama (ports 8080/11434); ZeroClaw Docker requires 172.17.0.1:11434 |
| **Together.ai** | ❌ | ✅ | ❌ | Free tier / paid | Custom provider; includes MiniMax (narrative synthesis) |
| **MiniMax (via Together.ai)** | ❌ | ✅ | ❌ | Free tier / paid | Narrative synthesis model (stonkmode) |
| **OpenAI** | ❌ | ✅ | ❌ | Paid | Custom provider |
| **Google Gemini** | ❌ | ✅ | ❌ | Paid | Custom provider |
| **NVIDIA NGC** | ❌ | ✅ | ❌ | Enterprise | Custom provider (NVIDIA employees) |
| **Disabled** | ✅ | ✅ | ✅ | Free | Python output only (no LLM synthesis) |

---

## Advanced & Optional Features

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|
| **Subagent verification** | ✅ Optional | ❌ | ❌ | Spawn verification agents for high-confidence analysis |
| **HMAC audit fingerprints** | ✅ Optional | ✅ Optional | ✅ Optional | Cryptographic proof of synthesis integrity |
| **Professional mode** | ❌ | ✅ Optional | ✅ Optional | FA Professional: Relaxed guardrails for advisor deployments |
| **Conversation history** | ✅ | ❌ | ❌ | Multi-turn Q&A within same context (Claude Code feature) |

---

## Integration & Compatibility

| Feature | Claude Code | OpenClaw | ZeroClaw | Hermes Agent | Notes |
|---------|---|---|---|---|
| **Works offline** | Partially | ✅ | ✅ | Full offline with local Ollama/llama-server; Claude Code needs API |
| **CI/CD friendly** | ✅ | ✅ | ✅ | Python script invocation |
| **Docker compatible** | ✅ | ✅ | ✅ Docker required | Can containerize for deployment |
| **Cloud-native** | ✅ | Optional | ❌ | Claude Code naturally cloud; OpenClaw can be; ZeroClaw ARM/Pi only |
| **On-premises** | ❌ | ✅ | ✅ | Full local deployment with GPU (OpenClaw/ZeroClaw) |
| **Regulated industries** | Partial | ✅ | ✅ | Claw platforms with local inference for compliance |
| **ARM/Raspberry Pi** | ❌ | ❌ | ✅ | ZeroClaw optimized for Pi 4/5 |
| **Enterprise guardrails** | ✅ | ✅ Optional | ✅ Optional | Educational mode always; professional mode available |

---

## Summary by Use Case

### Individual Investor (Home Use)
**Best:** Claude Code  
**Why:** Simple setup (no config), conversational Q&A, visual dashboards, no server management

**Key features:**
- ✅ One-command install (Claude auto-discovers)
- ✅ Multi-turn conversation ("Why is tech concentrated?" → Claude explains)
- ✅ Interactive dashboard (pie, sectors, sparklines, simulator)
- ✅ Vision extraction (upload broker statement screenshot → auto-extracted holdings)
- ✅ Stonkmode entertainment

---

### Financial Advisor (Professional Use)
**Best:** Either platform (depends on your infrastructure)

**Claude Code path:**
- ✅ Client uploads CSV → instant analysis + dashboard
- ✅ Vision extraction (client screenshots)
- ✅ Conversation history for review

**OpenClaw path:**
- ✅ Professional guardrails (relaxed for advisor oversight)
- ✅ HMAC audit fingerprints per analysis
- ✅ Multi-client batch processing
- ✅ CSV/Excel exports for client files

---

### Regulated Compliance (No External Cloud Transmission)
**Best:** OpenClaw with local Ollama/llama-server  
**Why:** Everything stays on-premises, zero external API calls except yfinance

**Setup:**
```bash
/portfolio llm-config
# Select: Local Ollama or llama-server
```

**Features:**
- ✅ Local GPU inference only
- ✅ HMAC audit fingerprints
- ✅ File-based output (CSV, HTML)
- ✅ No cloud provider access

---

### Lowest Cost / Self-Hosted
**Best:** OpenClaw or ZeroClaw with local Ollama (if you have GPU)  
**Why:** Free tier once GPU is configured, no recurring subscription

**Setup:** Requires 24GB+ VRAM GPU for larger models (RTX 4500 Ada, H100, etc.)

**Cost:** Hardware only + free Ollama

---

### Edge / IoT / ARM Devices
**Best:** ZeroClaw on Raspberry Pi 4/5  
**Why:** Optimized for minimal resources, Docker sandbox, no cloud required

**Setup:**
- Raspberry Pi 4 (8GB RAM minimum)
- Local Groq API key (or local Ollama with smaller model)
- 10-minute install

**Features:**
- ✅ Full portfolio analysis on $75 hardware
- ✅ Works offline with local Ollama
- ✅ Docker-sandboxed execution
- ⚠️ Slower response time (~5-10s due to CPU inference)

---

See `PLATFORM_COMPARISON.md` for detailed platform differences. See `COMMAND_INDEX.md` for all available commands.
